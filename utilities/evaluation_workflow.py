from init.google_ai import google_client
from google.genai import types

from utilities.parsing import repair_json
from utilities.storage import save_data, get_data
from utilities.vector_storage import query_vectors

from data.models import Message

import base64
import json
import uuid


def initialize_evaluation_workflow(user_message: Message) -> str:
    # Retrieve user profile information
    user_profile = ''
    user_profile_data = get_data(f'users/{user_message.phone_number}/profile')
    if user_profile_data:
        user_profile = f'This is my academic profile: {user_profile_data}'

    # Retrieve context information
    context_text = ''
    context_content = ''
    context_image = ''
    if user_message.context:
        context_data = get_data(f'users/{user_message.phone_number}/messages/{user_message.context.replace("wamid.", "")}')
        if context_data:
            context_text = f'Use this message as a reference when creating my evaluation: {context_data['text']}'
            if context_data['message_type'] == 'document' and context_data['media_content']:
                context_content = f'This document is attached to the reference message: {context_data['media_content']}'
            elif context_data['message_type'] == 'image' and context_data['media_content']:
                context_content = f'The accompanying image is attached to the reference message.'
                context_image = context_data['media_content']

    # Retrieve relevant memories
    relevant_memories = ''
    memories_data = query_vectors(data=user_message.text, user=user_message.phone_number)
    if memories_data:
        relevant_memories = f'These memories are relevant to the creation of my evaluation: {memories_data}'

    # Retrieve file content
    file_content = ''
    if user_message.message_type == 'document' and user_message.media_content:
        file_content = f'Use this document in the creation of my evaluation: {user_message.media_content}'

    system_prompt = f'''
        You are an evaluation generator specialized in creating progressive-difficulty assessments. You will generate exactly 10 questions based on the provided topic, starting with foundational concepts and gradually increasing in complexity. Your response must be strictly in the specified JSON format with no additional text.

        # REQUIREMENTS
        - Generate exactly 10 questions
        - Start with basic concepts (questions 1-3)
        - Progress to intermediate applications (questions 4-7)
        - End with advanced concepts and analysis (questions 8-10)
        - Each question must include a detailed explanation
        - All answers must be unambiguous
        - Options must be plausible and distinct
        - Follow the exact JSON structure provided

        # RESPONSE TEMPLATE
        {{"questions": [{{"id": "[unique sequential number]", "question": "[clear, specific question]", "options": {{"a": "[option text]", "b": "[option text]", "c": "[option text]", "d": "[option text]"}}, "correct": "[a,b,c, or d]", "explanation": "[detailed explanation of correct answer]"}}]}}
    '''

    user_prompt = f'''
        # EVALUATION TOPIC
        {user_message.text}
        {context_text}
        {context_content}
        {relevant_memories}
        {file_content}
        {user_profile}
    '''

    contents = [user_prompt]
    if user_message.message_type == 'image':
        user_image_data = base64.b64decode(user_message.media_content)
        contents.append(types.Part.from_bytes(data=user_image_data, mime_type='image/png'))
    if context_image:
        context_image_data = base64.b64decode(context_image)
        contents.append(types.Part.from_bytes(data=context_image_data, mime_type='image/png'))

    response = google_client.models.generate_content(
        model='gemini-2.0-flash',
        # model='learnlm-1.5-pro-experimental',
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.3,
        ),
    )

    user_message.tokens += response.usage_metadata.total_token_count
    user_message.input_tokens += response.usage_metadata.prompt_token_count
    user_message.output_tokens += response.usage_metadata.candidates_token_count
    
    evaluation_id = str(uuid.uuid4())
    evaluation_url = f'users/{user_message.phone_number}/evaluations/{evaluation_id}'
    raw_evaluation = response.text
    repaired_evaluation = repair_json(raw_evaluation)
    evaluation = json.loads(repaired_evaluation)

    save_data(evaluation_url, evaluation)

    return evaluation_id
