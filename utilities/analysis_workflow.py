from init.openai import openai_client

from data.models import Message

from utilities.storage import get_data
from utilities.vector_storage import get_vectors

import time


image_model = 'accounts/fireworks/models/llama-v3p2-90b-vision-instruct'
text_model = 'accounts/fireworks/models/llama-v3p3-70b-instruct'


def initialize_analysis_workflow(user_message: Message) -> str:
    timestamp = time.time() - 604800

    # Retrieve user profile information
    user_profile = ''
    user_profile_data = get_data(f'users/{user_message.phone_number}/profile')
    if user_profile_data:
        user_profile = f'Adapt the analysis to the student\'s profile: {user_profile_data}'
        print(user_profile)
    
    memories_data = get_vectors(user=user_message.phone_number, timestamp=timestamp)
    relevant_memories = ''
    if memories_data:
        relevant_memories = f'These memories are relevant to the student\'s current analysis request: {memories_data["documents"]}'
        print(relevant_memories)

    system_message = f'''
        Generate an actionable student progress analysis that strictly follows this format:

        <LEARNING_ANALYSIS>
        ## Current Snapshot
        - Subject Areas: [List key subjects/topics]
        - Learning Stage: [Current level + prerequisites met]
        - Time Frame: [Period covered by analysis]

        💡 Want to understand your starting point better? Ask me:
        - "Can you break down my current level in [subject]?"
        - "What prerequisites might I need to review?"

        ## Learning Patterns
        ### Strengths Observed
        [List of 4-5 specific learning approaches that work well]

        ### Growth Areas
        [List of 3-4 specific challenges with observed patterns]

        💡 Looking to understand your learning style? Ask me:
        - "Why does [pattern] work well for me?"
        - "How can I build on my strength in [area]?"
        - "What causes me to struggle with [challenge]?"

        ## Strategic Development Plan

        ### Short-Term Goals (Next 2-4 weeks)
        [3-4 specific, measurable objectives]

        ### Learning Strategies
        [4-5 personalized approaches tied to observed patterns]

        💡 Need strategy guidance? Ask me:
        - "Can you create a practice plan for [goal]?"
        - "How should I modify [strategy] for my style?"
        - "What's a good way to track my progress?"

        ## Action Steps

        For the Student:
        [5 specific, achievable tasks]

        For Support System:
        [3-4 concrete ways others can help]

        💡 Ready to take action? Ask me:
        - "Can you break down [task] into smaller steps?"
        - "How do I know if I'm making progress?"
        - "What should I do if I get stuck?"

        ## Progress Indicators
        [3-4 measurable metrics with clear checkpoints]

        💡 Want to track effectively? Ask me:
        - "How do I measure [indicator]?"
        - "What's a good checkpoint schedule?"
        - "Can you help me assess my current level?"

        ## Next Steps & Resources
        [List of immediate actions and supporting materials]

        💡 Remember: I can help you:
        - Break down complex topics
        - Create practice exercises
        - Analyze your progress
        - Adjust strategies as needed
        - Connect concepts to your interests
        - Develop deeper understanding

        ## Personal Notes
        [Specific observations about learning style and motivation]

        💡 Want to dig deeper? Ask me:
        - "How does my learning style affect my approach?"
        - "What motivational strategies might work for me?"
        - "How can I maintain momentum?"
        </LEARNING_ANALYSIS>

        # IMPORTANT
        - Present content directly without tags, hints or technical elements
        - Use clear, standard formatting and headings throughout
        - Write in the same language as the user's message
        - Include only content relevant to the analysis
        - Maintain consistent structure between sections

        RELEVNAT CONTEXT:
        {relevant_memories}
        {user_profile}
    '''

    model = text_model
    content = [{'type': 'text', 'text': system_message}]

    if user_message.media_content and user_message.message_type == 'image':
        model = image_model
        content.insert(0, {'type': 'image_url', 'image_url': {'url': f'data:image/jpeg;base64,{user_message.media_content}'}})

    response = openai_client.chat.completions.create(model=model, messages=[{'role': 'system', 'content': content}])

    print('TOTAL ANALYSIS TOKENS')
    user_message.tokens += response.usage.total_tokens
    print(user_message.tokens)

    return response.choices[0].message.content





