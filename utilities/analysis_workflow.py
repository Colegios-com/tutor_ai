from init.openai import openai_client

from utilities.storage import get_data
from utilities.vector_storage import query_vectors


image_model = 'accounts/fireworks/models/llama-v3p2-90b-vision-instruct'
text_model = 'accounts/fireworks/models/llama-v3p3-70b-instruct'


def initialize_analysis_workflow(phone_number) -> str:
    messages = get_data(f'users/{phone_number}/messages')
    previous_message = ''
    if messages:
        _, value = messages.popitem()
        previous_message = f'Previous Message: {value["text"]}'
    
    context = query_vectors(user=phone_number)
    relevant_context = ''
    if context:
        relevant_context = f'Relevant Context: {context}'

    system_message = f'''
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
        5. Respond in the answer of the current message.

        # FORMAT
        1. Respond in markdown format.
        2. Do not use LaTeX formatting.

        {"# IMPORTANT: Always structure your response in two sections: ANSWER and LOGICAL ANALYSIS." if debug else ''}

        # INTERACTION
        {relevant_context}
    '''

    model = text_model
    content = [{'type': 'text', 'text': system_message}]

    response = openai_client.chat.completions.create(model=model, messages=[{'role': 'system', 'content': content}])

    return response.choices[0].message.content





