from init.google_ai import google_client
from google.genai import types

from utilities.parsing import repair_json
from storage.storage import save_data, get_data, download_file
from storage.vector_storage import query_vectors

from data.models import Message

import base64
import json
import uuid


def initialize_evaluation_workflow(user_message: Message) -> str:
    contents = []

    # Get user profile for context
    profile_data = get_data(f'users/{user_message.phone_number}/profile')
    if profile_data:
        profile_text = f'Student Profile: {profile_data}'
        contents.append(types.Part.from_text(text=profile_text))

    # Retrieve context information
    if user_message.context:
        parts = []
        context_data = get_data(f'users/{user_message.phone_number}/messages/{user_message.context.replace("wamid.", "")}')
        if context_data:
            context_text = f'My current message is referencing this message: {context_data['text']}'
            parts.append(types.Part.from_text(text=context_text))
            if context_data['message_type'] == 'document':
                context_content = f'The accompanying document is attached to the reference message.'
                parts.append(types.Part.from_text(text=context_content))
                file = download_file(context_data['media_url'])
                parts.append(types.Part.from_bytes(data=file, mime_type=context_data['media_mime_type']))
            elif context_data['message_type'] == 'image':
                context_content = f'The accompanying image is attached to the reference message.'
                parts.append(types.Part.from_text(text=context_content))
                file = download_file(context_data['media_url'])
                parts.append(types.Part.from_bytes(data=file, mime_type=context_data['media_mime_type']))
            elif context_data['message_type'] == 'video':
                context_content = f'The accompanying video is attached to the reference message.'
                parts.append(types.Part.from_text(text=context_content))
                file = download_file(context_data['media_url'])
                parts.append(types.Part.from_bytes(data=file, mime_type=context_data['media_mime_type']))
            role = 'user' if context_data['sender'] == 'user' else 'model'
            contents.append(types.Content(parts=parts, role=role))

    # Retrieve relevant memories if no context is provided
    if not user_message.context:
        memories = query_vectors(data=user_message.text, user=user_message.phone_number)
        for memory_data in memories:
            memory_text = f'This memory is relevant to my current message: {memory_data}'
            contents.append(types.Part.from_text(text=memory_text))

    user_prompt = f'''
        This is my current message: {user_message.text}
    '''

    parts = []
    parts.append(types.Part.from_text(text=user_prompt))

    if user_message.message_type == 'image':
        file = download_file(user_message.media_url)
        parts.append(types.Part.from_bytes(data=file, mime_type=user_message.media_mime_type))
    elif user_message.message_type == 'video':
        file = download_file(user_message.media_url)
        parts.append(types.Part.from_bytes(data=file, mime_type=user_message.media_mime_type))
    elif user_message.message_type == 'document':
        file = download_file(user_message.media_url)
        parts.append(types.Part.from_bytes(data=file, mime_type=user_message.media_mime_type))

    contents.append(types.Content(parts=parts, role='user'))

    system_prompt = f'''
        You are an evaluation generator specialized in creating progressive-difficulty assessments. You will generate exactly 10 questions based on the provided topic, starting with foundational concepts and gradually increasing in complexity. Your response must be strictly in the specified JSON format with no additional text.

        # REQUIREMENTS
        - The evaluation must be in the same language as the user's message and provided context
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
