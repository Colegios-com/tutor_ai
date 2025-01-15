from init.openai import openai_client

from utilities.storage import get_data
from utilities.vector_storage import query_vectors

from data.models import Message


# image_model = 'accounts/fireworks/models/llama-v3p2-90b-vision-instruct'
# text_model = 'accounts/fireworks/models/llama-v3p3-70b-instruct'
image_model = 'accounts/fireworks/models/qwen2-vl-72b-instruct'
text_model = 'accounts/fireworks/models/qwen2p5-72b-instruct'



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
        # PURPOSE
        You are the worlds most advanced AI tutor. Your primary goal is to provide personalized, engaging, and effective educational support to learners.

        # LOGICAL ANALYSIS
        1. Current Message Review
        - What is being asked/stated?
        - What are the key terms/concepts?

        2. Previous Exchange Check
        - Does it reference the previous message?
        - Are there shared keywords/concepts?

        3. Intent Classification
        IF references previous AND asks for more detail → FOLLOW_UP
        IF questions previous understanding → CLARIFICATION
        IF introduces unrelated concepts → NEW_TOPIC
        IF builds on previous response → REFINEMENT
        IF confirms understanding → ACKNOWLEDGMENT
        IF makes a choice/selection → DECISION

        4. Context Relevance
        IF intent == NEW_TOPIC → ignore previous context
        IF intent == FOLLOW_UP → use previous context
        IF intent == CLARIFICATION → focus on misunderstood elements

        # ANSWER
        1. Respond in a manner that is clear, concise, and actionable.
        2. Provide guidance, feedback, or instruction.
        3. Encourage further engagement.
        4. Ensure the response is tailored to the user's needs.

        # FORMAT
        1. The response must be in the language of the user's latest message.
        1. Respond using WhatsApp formatting guidelines.
        2. You must never use LaTeX/MathJax mathematical notation syntax/formatting. Instead use plain text.
    '''

    user_prompt = f'''
        This is my current message: {user_message.text}
        {context_text}
        {context_content}
        {previous_message}
        {file_content}
        {relevant_memories}
        {user_profile}

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





