from init.openai import openai_client

from data.models import Message

from utilities.embedding import embed_data
from utilities.storage import save_data
from utilities.vector_storage import query_vectors, save_vectors


image_model = 'accounts/fireworks/models/llama-v3p2-90b-vision-instruct'
text_model = 'accounts/fireworks/models/llama-v3p3-70b-instruct'


def initialize_memory_workflow(message: Message, response: Message) -> str:
    message_url = f'users/{message.phone_number}/messages/{message.id.replace('wamid.', '')}'
    response_url = f'users/{message.phone_number}/messages/{response.id.replace('wamid.', '')}'
    save_data(message_url, message.dict())
    save_data(response_url, response.dict())
    
    context = query_vectors(data=message.text, user=message.phone_number)
    relevant_context = ''
    if context:
        relevant_context = f'Relevant Context: {context}'
    
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
        1. Include only the MOST actionable insight
        2. Must influence future teaching

        # INTERACTION
        User Message: {message.text}
        Tutor Response: {response.text}
        {relevant_context}
    '''

    model = text_model
    content = [{'type': 'text', 'text': system_message}]

    if message.media_content:
        model = image_model
        content.append({'type': 'image_url', 'image_url': {'url': f"data:image/jpeg;base64,{message.media_content}"}})

    response = openai_client.chat.completions.create(model=model, messages=[{'role': 'system', 'content': content}])

    memory = response.choices[0].message.content
    embeddings = embed_data([memory])
    metadata = {'user': message.phone_number, 'context_type': 'general'}
    if message.media_id:
        metadata['media_id'] = message.media_id
    save_vectors(metadata=metadata, data=[memory], embeddings=embeddings)
