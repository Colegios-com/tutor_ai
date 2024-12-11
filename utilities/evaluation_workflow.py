from init.openai import openai_client

from utilities.parsing import repair_json
from utilities.storage import save_data

from data.models import Message

import json
import uuid


image_model = 'accounts/fireworks/models/llama-v3p2-90b-vision-instruct'
text_model = 'accounts/fireworks/models/llama-v3p3-70b-instruct'


def initialize_evaluation_workflow(message: Message) -> str:

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
        {message.text}
    '''

    model = text_model
    content = [{'type': 'text', 'text': system_message}]

    response = openai_client.chat.completions.create(model=model, messages=[{'role': 'system', 'content': content}])

    print('TOTAL TOKENS')
    print(response.usage.total_tokens)
    evaluation_id = str(uuid.uuid4())
    evaluation_url = f'users/{message.phone_number}/evaluations/{evaluation_id}'
    raw_evaluation = response.choices[0].message.content
    repaired_evaluation = repair_json(raw_evaluation)
    evaluation = json.loads(repaired_evaluation)

    save_data(evaluation_url, evaluation)

    return evaluation_id





