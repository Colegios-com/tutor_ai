from init.google_ai import google_client
from google.genai import types

from data.models import Message

from utilities.storage import get_data
from utilities.vector_storage import get_vectors

import base64
import time


def initialize_analysis_workflow(user_message: Message) -> str:
    timestamp = time.time() - 604800

    # Retrieve user profile information
    user_profile = ''
    user_profile_data = get_data(f'users/{user_message.phone_number}/profile')
    if user_profile_data:
        user_profile = f'This is my academic profile: {user_profile_data}'
    
    memories_data = get_vectors(user=user_message.phone_number, timestamp=timestamp)
    relevant_memories = ''
    if memories_data:
        relevant_memories = f'These memories from the past 7 days are relevant to creation of my analysis: {memories_data["documents"]}'

    system_prompt = f'''
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

    user_prompt = f'''
        RELEVNAT CONTEXT:
        {relevant_memories}
        {user_profile}
    '''

    if user_message.message_type == 'image':
        image_data = base64.b64decode(user_message.media_content)
        contents=[user_prompt, types.Part.from_bytes(data=image_data, mime_type='image/png')]
    else:
        contents = user_prompt

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

    return response.text
