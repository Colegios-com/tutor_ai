from init.together import together_client

from utilities.embedding import embed_data
from utilities.parsing import repair_json_response
from utilities.storage import save_data
from utilities.vector_storage import save_vectors

from data.models import Message

import json

llama405bt = 'meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo'
llama90bt = 'meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo'


# Message History
async def save_message(message, response):
    # Object Storage
    url = f'users/{message.phone_number}/messages'
    save_data(url, message.dict())
    save_data(url, response.dict())


# Context History
def select_context_types(message, response):
    prompt = f'''
        You are a Pedagogic Memory Expert that analyzes educational interactions to identify meaningful memories that should be recorded.

        AVAILABLE MEMORY TYPES:
        - personal_profile: Student behavior, preferences, reactions
        - academic_context: Current studies, methods, progress  
        - knowledge_state: Subject comprehension, application
        - learning_events: Breakthroughs, significant moments

        USER INPUT:
        {message.text}

        IMAGE ANALYSIS:
        {message.image_analysis}

        TUTOR RESPONSE:
        {response.text}

        RESPONSE FORMAT:
        You must respond in a pipe separated string with the memory types in the order they should be executed.
        Example: personal_profile|knowledge_state|learning_events

        IMPORTANT:
        - Do not include memory types that are not part of the available memory types
        - Do not include text other than the pipe separated string of memory types in your response
        - Do not include any additional information or comments
    '''
    raw_response =  together_client.batch_response(prompt=prompt, image_base64=message.image, model=llama405bt, max_tokens=1500)
    return raw_response['response']


def generate_memory(message, response, context_type) -> str:
    if context_type == 'personal_profile':
        prompt = f'''
            You are a Pedagogic Memory Expert focused on observing student behavioral patterns and preferences.

            MEMORY TYPE: Personal Profile
            Purpose: Record meaningful insights about student behavior, preferences, and reactions to learning.

            MEMORY COMPOSITION:
            # Content: Observed behavior, preference, or reaction
            ## Context: When/how this was demonstrated in the interaction

            USER INPUT:
            {message.text}

            IMAGE ANALYSIS:
            {message.image_analysis}

            TUTOR RESPONSE:
            {response.text}

            RESPONSE FORMAT:
            # MEMORY_CONTENT ## MEMORY_CONTEXT
        '''
    elif context_type == 'academic_context':
        prompt = f'''
            You are a Pedagogic Memory Expert focused on tracking educational progress and methodology.

            MEMORY TYPE: Academic Context
            Purpose: Record insights about current studies, learning methods, and academic progress.

            MEMORY COMPOSITION:
            # Content: Observed study approach, method used, or progress indicator
            ## Context: When/how this manifested in the interaction

            USER INPUT:
            {message.text}

            IMAGE ANALYSIS:
            {message.image_analysis}

            TUTOR RESPONSE:
            {response.text}

            RESPONSE FORMAT:
            # MEMORY_CONTENT ## MEMORY_CONTEXT
        '''
    elif context_type == 'knowledge_state':
        prompt = f'''
            You are a Pedagogic Memory Expert focused on assessing subject understanding.

            MEMORY TYPE: Knowledge State
            Purpose: Record evidence of subject comprehension and concept application.

            MEMORY COMPOSITION:
            # Content: Demonstrated understanding or application of knowledge
            ## Context: How this understanding was shown in the interaction

            USER INPUT:
            {message.text}

            IMAGE ANALYSIS:
            {message.image_analysis}

            TUTOR RESPONSE:
            {response.text}

            RESPONSE FORMAT:
            # MEMORY_CONTENT ## MEMORY_CONTEXT
        '''
    elif context_type == 'learning_events':
        prompt = f'''
            You are a Pedagogic Memory Expert focused on identifying significant learning moments.

            MEMORY TYPE: Learning Events
            Purpose: Record breakthroughs, revelations, and significant learning achievements.

            MEMORY COMPOSITION:
            # Content: The breakthrough or significant learning moment
            ## Context: What led to or demonstrated this achievement

            USER INPUT:
            {message.text}

            IMAGE ANALYSIS:
            {message.image_analysis}

            TUTOR RESPONSE:
            {response.text}

            RESPONSE FORMAT:
            # MEMORY_CONTENT ## MEMORY_CONTEXT
        '''

    raw_response =  together_client.batch_response(prompt=prompt, image_base64=message.image, model=llama405bt, max_tokens=1500)
    return raw_response['response']


async def initialize_memory_workflow(message, response):
    raw_context_types = select_context_types(message, response)
    context_types = raw_context_types.split('|')


    for context_type in context_types:
        memory = generate_memory(message, response, context_type)

        embeddings = embed_data([memory])
        metadata = {'user': message.phone_number, 'context_type': context_type}
        if message.image_id:
            metadata['image_id'] = message.image_id
        save_vectors(metadata=metadata, data=[memory], embeddings=embeddings)
