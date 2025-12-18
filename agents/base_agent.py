from init.google_ai import google_client
from google.genai import types

from data.models import Message

from storage.storage import get_active_conversation, build_conversation_history

from demos.custormer_service import get_system_prompt, functions
from demos.router import router_system_prompt, router_functions


def build_contents(user_message: Message) -> list[types.Content]:
    contents = []

    parts = []
    parts.append(types.Part.from_text(text=f'My phone number id is: {user_message.wa_id}. Please use it to identify me during our interaction.'))
    if user_message.bot_id:
        parts.append(types.Part.from_text(text=f'Your bot id is: {user_message.bot_id}. Please use it when performing any actions during our interaction.'))
    

    message_history = build_conversation_history(user_message)

    if message_history:
        for message in message_history:
            parts = []
            if message.file:
                parts.append(types.Part.from_uri(file_uri=message.file.uri, mime_type=message.file.mime_type))
            if message.text:
                parts.append(types.Part.from_text(text=message.text))

            contents.append(
                types.Content(parts=parts, role=message.sender)
            )

    parts = []
    if user_message.file:
        parts.append(types.Part.from_uri(file_uri=user_message.file.uri, mime_type=user_message.file.mime_type))
    if user_message.text:
        parts.append(types.Part.from_text(text=user_message.text))
    contents.append(
        types.Content(parts=parts, role=user_message.sender)
    )
    
    return contents


def build_agent(user_message: Message) -> tuple[str, list[types.Tool], list[types.Content]]:
    active_conversation = get_active_conversation(user_message)
    if not active_conversation:
        print('No active conversation found, sending to router.')
        system_prompt = router_system_prompt
        contents = build_contents(user_message)
        tools = router_functions
        tool_declarations = [f['decalration'] for f in router_functions.values()]
        return system_prompt, tools, tool_declarations, contents

    print('Active conversation found, sending to customer service bot.')
    user_message.conversation_id = active_conversation['id']
    user_message.bot_id = active_conversation['bots']['id']
    user_message.restaurant_id = active_conversation['bots']['restaurant_id']
    system_prompt = get_system_prompt(user_message)
    contents = build_contents(user_message)
    tools = functions
    tool_declarations = [f['decalration'] for f in functions.values()]
    return system_prompt, tools, tool_declarations, contents


def initialize_base_agent(user_message: Message) -> str:
    # 1. Build initial history
    system_prompt, tools, tool_declarations, contents = build_agent(user_message)
    
    # 2. Define Tools
    # Ensure your 'functions' dict has the raw 'declaration' (fixed typo from 'decalration')
    
    print('Execution loop started.')
    
    # Main Agent Loop
    for iteration in range(20):
        print(f"\n🔄 Iteration {iteration + 1}")
                    
        # 3. Generate Content
        try:
            response = google_client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    tools=[types.Tool(function_declarations=tool_declarations)],
                )
            )
        except Exception as e:
            print(f"❌ Error generating content: {e}")
            return "I'm sorry, I'm having trouble connecting right now."

        if not response.candidates:
            return "No response from model."

        # 5. Capture the Model's Response Parts (Includes Thought Signatures)
        model_parts = response.candidates[0].content.parts
        
        # --- THOUGHT SIGNATURE HANDLING ---
        # The SDK objects in 'model_parts' already contain the .thought_signature attribute.
        # We don't need to manually extract and re-inject it, simply appending 
        # these specific Part objects to the history preserves the signature.
        
        # Debugging: Verify signature presence
        thoughts_detected = False
        for part in model_parts:
            # Check attribute existence safely
            sig = getattr(part, 'thought_signature', None)
            if sig:
                print(f"🔐 Thought Signature Detected: {sig[:30]}...")
                thoughts_detected = True
        
        if not thoughts_detected and iteration > 0:
            print("⚠️ Note: No thought signature in this turn.")
        # ----------------------------------

        # 6. Update History (Critical: This saves the signature for the next turn)
        contents.append(
            types.Content(parts=model_parts, role="model")
        )
        
        # 7. Process Parts for Function Calls vs Final Text
        function_calls = []
        final_text_parts = []

        for part in model_parts:
            # Check for Function Call
            if hasattr(part, 'function_call') and part.function_call:
                function_calls.append(part.function_call)
            
            # Check for Text (Final Answer)
            if hasattr(part, 'text') and part.text:
                final_text_parts.append(part.text)

        # 8. Handle Execution or Return
        if function_calls:
            print(f'🤖 Model triggered {len(function_calls)} function(s)')
            
            function_responses = []
            
            # Execute all functions requested in this turn (Parallel Calling)
            for function_call in function_calls:
                fn_name = function_call.name
                fn_args = function_call.args
                
                print(f'   > Calling: {fn_name} with args: {fn_args}')
                
                if fn_name in tools:
                    try:
                        # Call the Python function
                        result = tools[fn_name]['function'](user_message, **fn_args)
                        
                        # Pack response
                        function_responses.append(
                            types.Part.from_function_response(
                                name=fn_name,
                                response={"result": str(result)}
                            )
                        )
                    except Exception as e:
                        # Handle tool errors gracefully so the bot doesn't crash
                        error_msg = f"Error executing {fn_name}: {str(e)}"
                        print(f"   ❌ {error_msg}")
                        function_responses.append(
                            types.Part.from_function_response(
                                name=fn_name,
                                response={"error": error_msg}
                            )
                        )
                else:
                    print(f"   ❌ Function {fn_name} not found in tools.")

            # Append function results to history
            # The next loop iteration will now send:
            # [User Message] -> [Model Call + Signature] -> [Function Result]
            contents.append(
                types.Content(parts=function_responses, role="user") # Function responses are technically 'user' role in Vertex
            )
            
        else:
            # No function calls? We are done.
            print('✅ Execution loop finalized.')
            return "".join(final_text_parts)

    return "Max iterations reached."