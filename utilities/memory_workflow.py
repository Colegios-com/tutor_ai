from init.openai import openai_client

from data.models import Message

from utilities.embedding import embed_data
from utilities.storage import save_data
from utilities.vector_storage import query_vectors, save_vectors


image_model = 'accounts/fireworks/models/llama-v3p2-90b-vision-instruct'
text_model = 'accounts/fireworks/models/llama-v3p3-70b-instruct'


def initialize_memory_workflow(user_message: Message, response_message: Message) -> str:    
    # Retrieve relevant memories
    relevant_memories = ''
    memories_data = query_vectors(data=user_message.text, user=user_message.phone_number)
    if memories_data:
        relevant_memories = f'These memories are relevant to the student\'s current message: {memories_data}'
        print(relevant_memories)

    # Retrieve file content
    file_content = ''
    if user_message.message_type == 'document' and user_message.media_content:
        file_content = f'The student has attached this document to their message: {user_message.media_content}'
        print(file_content)
    
    system_message = f'''
        # PURPOSE
        Extract the single most valuable teaching insight from this interaction that will meaningfully improve future responses.

        # LOGICAL ANALYSIS
        1. Examine Exchange
        - What was the student trying to achieve?
        - How did they approach it?
        - How effective was the response?

        2. Deterine CONTENT and CONTEXT
        - What was the key insight?
        - Why was it important?
        - How was it produced?

        3. Insight Classification
        IF demonstrates learning method/style → LEARNING_STYLE
        IF reveals knowledge gap/misconception → KNOWLEDGE_GAP
        IF shows mastery/understanding → COMPREHENSION
        IF indicates preferred explanation type → PREFERENCE
        IF highlights specific difficulty → CHALLENGE
        IF demonstrates progress/breakthrough → PROGRESS

        # FORMAT  
        Response must be in this format: # TYPE ## CONTENT ### CONTEXT

        # IMPORTANT
        - Include only the MOST actionable insight
        - Must influence future teaching
        - The insight must be in the language of the interaction

        # INTERACTION
        This is the student's latest message: {user_message.text}
        {file_content}
        This is the tutor's response message: {response_message.text}
        {relevant_memories}
    '''

    model = text_model
    content = [{'type': 'text', 'text': system_message}]

    if user_message.media_content and user_message.message_type == 'image':
        model = image_model
        content.append({'type': 'image_url', 'image_url': {'url': f'data:image/jpeg;base64,{user_message.media_content}'}})

    response = openai_client.chat.completions.create(model=model, messages=[{'role': 'system', 'content': content}])

    print('TOTAL MEMORY TOKENS')
    user_message.tokens += response.usage.total_tokens
    print(user_message.tokens)

    memory = response.choices[0].message.content
    embeddings = embed_data([memory])
    metadata = {'user': user_message.phone_number, 'context_type': 'general'}
    if user_message.media_id:
        metadata['media_id'] = user_message.media_id
    save_vectors(metadata=metadata, data=[memory], embeddings=embeddings)

    #TODO: Change from user id (instead of phone number) to jwt(phone).signature
    message_url = f'users/{user_message.phone_number}/messages/{user_message.id.replace('wamid.', '')}'
    response_url = f'users/{user_message.phone_number}/messages/{response_message.id.replace('wamid.', '')}'
    save_data(message_url, user_message.dict())
    save_data(response_url, response_message.dict())
