from init.openai import openai_client

from utilities.parsing import repair_json
from utilities.storage import save_data, get_data
from utilities.vector_storage import query_vectors

from data.models import Message

import json
import uuid


image_model = 'accounts/fireworks/models/llama-v3p2-90b-vision-instruct'
text_model = 'accounts/fireworks/models/llama-v3p3-70b-instruct'


def initialize_evaluation_workflow(user_message: Message) -> str:
    # Retrieve user profile information
    user_profile = ''
    user_profile_data = get_data(f'users/{user_message.phone_number}/profile')
    if user_profile_data:
        user_profile = f'The student\'s profile is as follows: {user_profile_data}'
        print(user_profile)

    # Retrieve context information
    context_text = ''
    context_content = ''
    context_image = ''
    if user_message.context:
        context_data = get_data(f'users/{user_message.phone_number}/messages/{user_message.context.replace("wamid.", "")}')
        if context_data:
            context_text = f'The student requests the evaluation to be generated based on this message: {context_data['text']}'
            print(context_text)
            if context_data['message_type'] == 'document' and context_data['media_content']:
                context_content = f'The attached document will serve as the basis for the evaluation, as specifically requested by the student: {context_data['media_content']}'
                print(context_content)
            elif context_data['message_type'] == 'image' and context_data['media_content']:
                context_content = f'The attached image will serve as the basis for the evaluation, as specifically requested by the student.'
                context_image = context_data['media_content']
                print(context_content)
                print(context_image)

    # Retrieve relevant memories
    relevant_memories = ''
    memories_data = query_vectors(data=user_message.text, user=user_message.phone_number)
    if memories_data:
        relevant_memories = f'These memories are relevant to the student\'s current evaluation request: {memories_data}'
        print(relevant_memories)

    # Retrieve file content
    file_content = ''
    if user_message.message_type == 'document' and user_message.media_content:
        file_content = f'The student has attached this document to be evaluated on: {user_message.media_content}'
        print(file_content)

    system_message = f'''
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

        # EVALUATION TOPIC
        {user_message.text}
        {context_text}
        {context_content}
        {relevant_memories}
        {file_content}
        {user_profile}
    '''

    model = text_model
    content = [{'type': 'text', 'text': system_message}]

    if context_image:
        model = image_model
        content.insert(0, {'type': 'image_url', 'image_url': {'url': f'data:image/jpeg;base64,{context_image}'}})

    response = openai_client.chat.completions.create(model=model, messages=[{'role': 'system', 'content': content}])

    print('TOTAL EXAM TOKENS')
    user_message.tokens += response.usage.total_tokens
    print(user_message.tokens)
    
    evaluation_id = str(uuid.uuid4())
    evaluation_url = f'users/{user_message.phone_number}/evaluations/{evaluation_id}'
    raw_evaluation = response.choices[0].message.content
    repaired_evaluation = repair_json(raw_evaluation)
    evaluation = json.loads(repaired_evaluation)

    save_data(evaluation_url, evaluation)

    return evaluation_id





