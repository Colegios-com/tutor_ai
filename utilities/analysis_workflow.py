from init.openai import openai_client

from data.models import Message

from utilities.storage import get_data
from utilities.vector_storage import get_vectors

import time


# image_model = 'accounts/fireworks/models/llama-v3p2-90b-vision-instruct'
# text_model = 'accounts/fireworks/models/llama-v3p3-70b-instruct'
image_model = 'accounts/fireworks/models/qwen2-vl-72b-instruct'
text_model = 'accounts/fireworks/models/qwen2p5-72b-instruct'


def initialize_analysis_workflow(user_message: Message) -> str:
    timestamp = time.time() - 604800

    # Retrieve user profile information
    user_profile = ''
    user_profile_data = get_data(f'users/{user_message.phone_number}/profile')
    if user_profile_data:
        user_profile = f'This is my academic profile: {user_profile_data}'
        print(user_profile)
    
    memories_data = get_vectors(user=user_message.phone_number, timestamp=timestamp)
    relevant_memories = ''
    if memories_data:
        relevant_memories = f'These memories from the past 7 days are relevant to creation of my analysis: {memories_data["documents"]}'
        print(relevant_memories)

    system_prompt = f'''
        Here is the modified analysis prompt that mirrors the guide prompt:

        You are a student progress analyst specialized in creating comprehensive learning analyses. You will generate a detailed examination of a student's current learning status, identifying strengths, weaknesses, and strategic development plans. Your response must be strictly in the specified format with no additional text.

        # REQUIREMENTS
        - Generate a comprehensive analysis that includes current snapshot, learning patterns, strategic development plan, action steps, progress indicators, next steps, and personal notes
        - Each section must specify its purpose and content
        - Include clear, measurable milestones for each learning component
        - Ensure logical progression of concepts
        - Include prerequisites and key questions for each section
        - Each section should represent a distinct aspect of the student's learning and development

        STRUCTURE
        # Current Snapshot
        - Subject Areas: [List key subjects/topics]
        - Learning Stage: [Current level + prerequisites met]
        - Time Frame: [Period covered by analysis]

        # Learning Patterns
        ## Strengths Observed
        [List of specific learning approaches that work well]

        # Growth Areas
        [List of specific challenges with observed patterns]

        # Strategic Development Plan
        ## Short-Term Goals (Next 2-4 weeks)
        [List of specific, measurable objectives]

        ## Learning Strategies
        [List of personalized approaches tied to observed patterns]

        # Action Steps
        For the Student: [List of specific, achievable tasks]
        For Support System: [List of concrete ways others can help]

        # Progress Indicators
        [List of measurable metrics with clear checkpoints]

        # Next Steps & Resources
        [List of immediate actions and supporting materials]

        # Personal Notes
        [Specific observations about learning style and motivation]

        NOTES
        - Each section should represent a logical aspect of the student's learning and development
        - Milestones should become more specific as you move deeper into the analysis
        - Key question lists should be relevant to the specific section's content
        - Prerequisites should clearly indicate what's needed before starting that section
        - Use clear, standard formatting and headings throughout
        - Write in the same language as the user's message
        - Include only content relevant to the analysis
        - Maintain consistent structure between sections
    '''

    user_prompt = '''
        RELEVNAT CONTEXT:
        {relevant_memories}
        {user_profile}
    '''

    model = text_model
    system_content = [{'type': 'text', 'text': system_prompt}]
    user_content = [{'type': 'text', 'text': user_prompt}]

    if user_message.media_content and user_message.message_type == 'image':
        model = image_model
        user_content.insert(0, {'type': 'image_url', 'image_url': {'url': f'data:image/jpeg;base64,{user_message.media_content}'}})

    response = openai_client.chat.completions.create(model=model, messages=[{'role': 'system', 'content': system_content}, {'role': 'user', 'content': user_content}])

    print('TOTAL ANALYSIS TOKENS')
    user_message.tokens += response.usage.total_tokens
    print(user_message.tokens)

    return response.choices[0].message.content





