from init.openai import openai_client

from data.models import Message

from utilities.storage import get_data
from utilities.vector_storage import get_vectors

import time


image_model = 'accounts/fireworks/models/llama-v3p2-90b-vision-instruct'
text_model = 'accounts/fireworks/models/llama-v3p3-70b-instruct'


def initialize_analysis_workflow(user_message: Message) -> str:
    timestamp = time.time() - 604800
    
    context = get_vectors(user=user_message.phone_number, timestamp=timestamp)
    relevant_context = ''
    if context:
        relevant_context = f'Relevant Context: {context}'

    print(relevant_context)

    system_message = f'''
        Generate student progress analysis (800-1000 words) with:

        # CONTENT
        - Academic Development: Subject progress, achievements, challenges
        - Social-Emotional: Peer interactions, leadership, regulation
        - Learning Strategies: Methods, tools, patterns
        - Development Areas: Current challenges with patterns and goals
        - Actionables: 5 student, 3 parent, 3 teacher tasks
        - Progress Indicators: 3-4 measurable metrics

        # TONE
        - Expert pedagogical voice
        - Links observations to developmental patterns
        - Connects different learning domains
        - Grounds recommendations in learning theory
        - Balances professional insight with accessibility
        - Frames challenges as growth opportunities

        # IMPORTANT
        - Format using detailed paragraphs for analysis, 4-6 bullet points for lists
        - Make all recommendations specific, achievable, and measurable
        - The analysis must be in the language of the relevant context

        Context:
        {relevant_context}
    '''

    model = text_model
    content = [{'type': 'text', 'text': system_message}]

    response = openai_client.chat.completions.create(model=model, messages=[{'role': 'system', 'content': content}])

    return response.choices[0].message.content





