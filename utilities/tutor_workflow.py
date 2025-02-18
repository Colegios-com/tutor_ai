from init.openai import openai_client

from utilities.storage import get_data
from utilities.vector_storage import query_vectors

from data.models import Message


image_model = 'accounts/fireworks/models/llama-v3p2-90b-vision-instruct'
text_model = 'accounts/fireworks/models/llama-v3p3-70b-instruct'
# image_model = 'accounts/fireworks/models/qwen2-vl-72b-instruct'
# text_model = 'accounts/fireworks/models/qwen2p5-72b-instruct'



def initialize_tutor_workflow(user_message: Message, debug=False) -> str:
    # Retrieve user profile information
    user_profile = ''
    profile_data = get_data(f'users/{user_message.phone_number}/profile')
    if profile_data:
        user_profile = f'This is my academic profile: {profile_data}'
        print(user_profile)

    # Retrieve context information
    context_text = ''
    context_content = ''
    if user_message.context:
        context_data = get_data(f'users/{user_message.phone_number}/messages/{user_message.context.replace("wamid.", "")}')
        if context_data:
            context_text = f'My current message is referencing this message: {context_data['text']}'
            print(context_text)
            if context_data['message_type'] == 'document' and context_data['media_content']:
                context_content = f'This document is attached to the message I am referencing: {context_data['media_content']}'
                print(context_content)

    # Retrieve previous message if no context is provided
    previous_message = ''
    if not context_text:
        previous_messages = get_data(f'users/{user_message.phone_number}/messages', order_by='timestamp', limit=1)
        if previous_messages:
            _, previous_message_data = previous_messages.popitem()
            previous_message = f'This is the last message you sent me: {previous_message_data['text']}'
            print(previous_message)

    # Retrieve relevant memories if no context is provided
    relevant_memories = ''
    if not context_text:
        memories_data = query_vectors(data=user_message.text, user=user_message.phone_number)
        if memories_data:
            relevant_memories = f'These memories are relevant to my current message: {memories_data}'
            print(relevant_memories)

    # Retrieve file content
    file_content = ''
    if user_message.message_type == 'document' and user_message.media_content:
        file_content = f'I have attached this docuent for you to analyze before providing a response: {user_message.media_content}'
        print(file_content)

    system_prompt = f'''
        # PURPOSE: Be a personalized, engaging AI tutor. Focus on clarity, adaptability, and actionable guidance.

        # CORE RULES  
        1. **Analysis Guidelines**  
        - Classify intent: 'Follow-up', 'Clarification', 'New Topic', or 'Refinement'.
        - Use prior context *only* when relevant.
        - For ambiguous user messages, especially single words, analyze accompanying context. If none or unclear, prompt for clarification.

        2. **Response Content Guidelines**
        - Never reference intent classification.
        - Respond in the same language as the user's current message.
        - *Prioritize brevity* and step-by-step explanations.
        - Use examples, analogies, and visuals to enhance understanding.
        - *Avoid* jargon, complex terms, or overly technical explanations.
        - Be as direct and clear as possible in responses.
        - Use emoji to engage the user.

        3. **Response Formatting**
        - **Emphasis**: Use *bold* or _italics_ to highlight important words or phrases.
        - **Code and Mathematical Expressions**: Enclose examples and mathematical expressions in `code` format.
        - **Quotes**: Start each quote on a new line, using the '>' symbol.

        4. **Math Formatting**: 
        - *Always* UTF-8 symbols for mathematical expressions.
        - *Never* use LaTeX or backslash formatting; use the appropriate UTF-8 symbol.
        - *Always* utilize subscript and superscript where appropriate, e.g., `x₁ + x₂ = 10`, `x² + y³ = zⁿ`.
        - *Never* use underscore (_) for subscripts; use the appropriate UTF-8 symbol.
        - *Examples*:
            - `½`, `5 × 3 = 15`, `10 ÷ 2 = 5`
            - `√2`, `∛8`, `∜16`
            - `∑ₙ₌₁^∞ xₙ`, `∏ₖ₌₁^10 k`, `∫₀¹ x² dx`
            - `dy/dx`, `∂f/∂x`, `limₙ→∞ (1 + 1/n)ⁿ = e`
            - `v = [v₁, v₂, v₃]`, `A = [[a₁₁, a₁₂], [a₂₁, a₂₂]]`
            - `P(A | B)`, `μ = 0`, `σ² = 1`
            - `sin(θ) + cos²(θ) = 1`, `F = ma`, `E = mc²`
            - `e^(iπ) + 1 = 0`, `x = (−b ± √(b² − 4ac))/(2a)`
            - `∫₀^∞ e⁻ˣ dx = 1`, `a ⋅ b = |a||b|cosθ`
            - `μ = (∑ₙ₌₁^N xₙ)/N`, `∇⋅F = ρ`, `∇×F = J`
            - `∇²f = 0`, `∂²u/∂t² = c²∇²u`
            - `a₁ + a₂ = 10`, `x₁² + x₂² = r²`
    '''

    user_prompt = f'''
        This is my current message: {user_message.text}
        {context_text}
        {context_content}
        {previous_message}
        {file_content}
        {relevant_memories}
        {user_profile}

        You must respond *DIRECTLY* and *CLEARLY* in the same language as my current message.
        You must *EXCLUSIVELY* use UTF-8 symbols for mathematical expressions.
        You must *NEVER* use LaTeX or backslash formatting in your response; use the appropriate UTF-8 symbol.
        You must *ALWAYS* utilize subscript and superscript where appropriate.
        You must *NEVER* use underscore (_) for subscripts; use the appropriate UTF-8 symbol.
    '''

    model = text_model
    system_content = [{'type': 'text', 'text': system_prompt}]
    user_content = [{'type': 'text', 'text': user_prompt}]

    if user_message.media_content and user_message.message_type == 'image':
        model = image_model
        user_content.insert(0, {'type': 'image_url', 'image_url': {'url': f'data:image/jpeg;base64,{user_message.media_content}'}})

    response = openai_client.chat.completions.create(model=model, messages=[{'role': 'system', 'content': system_content}, {'role': 'user', 'content': user_content}])

    print('TOTAL TUTOR TOKENS')
    user_message.tokens += response.usage.total_tokens
    print(user_message.tokens)

    return response.choices[0].message.content
