from init.openai import openai_client

from data.models import Message

from utilities.storage import get_data
from utilities.vector_storage import get_vectors

import time


image_model = 'accounts/fireworks/models/llama-v3p2-90b-vision-instruct'
text_model = 'accounts/fireworks/models/llama-v3p3-70b-instruct'


def initialize_analysis_workflow(message: Message) -> str:
    timestamp = time.time() - 604800
    
    context = get_vectors(user=message.phone_number, timestamp=timestamp)
    relevant_context = ''
    if context:
        relevant_context = f'Relevant Context: {context}'

    system_message = f'''
        # PURPOSE
        Generate concrete, actionable weekly feedback based on specific student interactions that can be immediately implemented by students, parents, and teachers.

        # LOGICAL ANALYSIS
        1. Interaction Pattern Analysis
        - What specific subject areas/topics appeared in this week's interactions?
        - Which concrete examples show student strengths or struggles?
        - What measurable outcomes were achieved or missed?

        2. Behavioral Evidence Review
        - What specific study habits were demonstrated?
        - Which learning strategies did the student use effectively/ineffectively?
        - What direct quotes or examples show understanding or confusion?

        # FORMAT
        # [PRIMARY_INSIGHT_TYPE]
        ## Key Findings This Week
        - Specific examples from interactions
        - Direct quotes showing patterns
        - Concrete measurement of performance

        ## Evidence and Impact
        1. What We Observed
        - [Specific interaction example]
        - [Measurable outcome]
        - [Student response/behavior]

        2. Why It Matters
        - [Direct impact on learning]
        - [Connection to curriculum]
        - [Effect on academic progress]

        ## Daily Action Plan
        For Student:
        - Monday: [Specific task with time and deliverable]
        - Tuesday: [Specific task with time and deliverable]
        [Continue for each day]

        For Parents:
        - Daily: [15-minute specific support activity]
        - Weekly: [Weekend review activity]
        - Resources: [Exact materials/tools needed]

        For Teachers:
        - Class adjustments: [Specific teaching modification]
        - Assessment changes: [Concrete grading/testing adaptation]
        - Support plan: [Precise intervention strategy]

        ## Success Metrics
        Target 1: [Specific, measurable outcome]
        - Current level: [Exact measure]
        - Week's goal: [Exact measure]
        - How to track: [Specific tracking method]

        [Repeat for 2-3 key metrics]

        # IMPORTANT
        1. Every observation must cite specific interaction
        2. All actions must be doable within 15-30 minutes
        3. Use student's actual words/work as examples
        4. Include only realistic, achievable weekly goals
        5. Provide exact resources/materials needed
        6. Write at appropriate reading level for audience

        # RELEVANT INTERACTIONS
        {relevant_context}
    '''

    model = text_model
    content = [{'type': 'text', 'text': system_message}]

    response = openai_client.chat.completions.create(model=model, messages=[{'role': 'system', 'content': content}])

    return response.choices[0].message.content





