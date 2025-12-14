from init.google_ai import google_client
from google.genai import types

from data.models import Message

from storage.storage import get_conversation

from demos.custormer_service import get_system_prompt, functions


def build_message_history(user_message: Message) -> list[types.Content]:
    # Get open conversations tied to the user and bots tied to the business phone number.
    # If ONE open convo, get that one and bot ID.
    # If none open, reroute to main bot associated with business phone number.
    # If multiple open, ask user to select one (leverage carousel menu).
    messages = []

    print(f"Building message history for phone number {user_message.phone_number_id}")
    message_history = get_conversation(user_message.phone_number_id)

    if message_history:
        for message in message_history:
            parts = []
            if message.file:
                parts.append(types.Part.from_uri(file_uri=message.file.uri, mime_type=message.file.mime_type))
            if message.text:
                parts.append(types.Part.from_text(text=message.text))

            messages.append(
                types.Content(parts=parts, role=message.sender)
            )

    parts = []
    parts.append(types.Part.from_text(text=f'My phone number id is: {user_message.phone_number_id}. Please use it to identify me during our interaction.'))
    if user_message.file:
        parts.append(types.Part.from_uri(file_uri=user_message.file.uri, mime_type=user_message.file.mime_type))
    if user_message.text:
        parts.append(types.Part.from_text(text=user_message.text))
    messages.append(
        types.Content(parts=parts, role=user_message.sender)
    )
    
    return messages



def initialize_base_agent(user_message: Message) -> str:
    # 1. Build initial history
    conversation = build_message_history(user_message)
    
    # 2. Define Tools
    # Ensure your 'functions' dict has the raw 'declaration' (fixed typo from 'decalration')
    tool_declarations = [f['decalration'] for f in functions.values()]
    tools = types.Tool(function_declarations=tool_declarations)
    
    print('Execution loop started.')
    
    # Main Agent Loop
    for iteration in range(20):
        print(f"\n🔄 Iteration {iteration + 1}")
        
        # 3. Configure generation
        config = types.GenerateContentConfig(
            tools=[tools],
            # Thought signatures are most effective when temperature is low for reasoning
            temperature=0.0 
        )
        
        system_prompt = get_system_prompt()
        config.system_instruction = system_prompt or 'You are a customer service bot.'
        
        # 4. Generate Content
        try:
            response = google_client.models.generate_content(
                model="gemini-3-pro-preview", # Ensure this model version supports Gemini 3 features
                contents=conversation,
                config=config
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
        conversation.append(
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
                
                print(f'   > Calling: {fn_name}')
                
                if fn_name in functions:
                    try:
                        # Call the Python function
                        result = functions[fn_name]['function'](**fn_args)
                        
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
            conversation.append(
                types.Content(parts=function_responses, role="user") # Function responses are technically 'user' role in Vertex
            )
            
        else:
            # No function calls? We are done.
            print('✅ Execution loop finalized.')
            return "".join(final_text_parts)

    return "Max iterations reached."