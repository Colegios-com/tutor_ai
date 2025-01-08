from init.openai import openai_client

from data.models import Message

from utilities.storage import get_data
from utilities.vector_storage import query_vectors

import time


image_model = 'accounts/fireworks/models/llama-v3p2-90b-vision-instruct'
text_model = 'accounts/fireworks/models/llama-v3p3-70b-instruct'


def initialize_guide_workflow(user_message: Message) -> str:
    # Retrieve user profile information
    user_profile = ''
    user_profile_data = get_data(f'users/{user_message.phone_number}/profile')
    if user_profile_data:
        user_profile = f'Adapt the study guide to the student\'s profile: {user_profile_data}'
        print(user_profile)

    # Retrieve context information
    context_text = ''
    context_content = ''
    context_image = ''
    if user_message.context:
        context_data = get_data(f'users/{user_message.phone_number}/messages/{user_message.context.replace("wamid.", "")}')
        if context_data:
            context_text = f'The student requests the study guide to be generated based on this message: {context_data['text']}'
            print(context_text)
            if context_data['message_type'] == 'document' and context_data['media_content']:
                context_content = f'The attached document will serve as the basis for the study guide, as specifically requested by the student: {context_data['media_content']}'
                print(context_content)
            elif context_data['message_type'] == 'image' and context_data['media_content']:
                context_content = f'The attached image will serve as the basis for the study guide, as specifically requested by the student.'
                context_image = context_data['media_content']
                print(context_content)
                print(context_image)

    # Retrieve relevant memories
    relevant_memories = ''
    memories_data = query_vectors(data=user_message.text, user=user_message.phone_number)
    if memories_data:
        relevant_memories = f'These memories are relevant to the student\'s current study guide request: {memories_data}'
        print(relevant_memories)

    # Retrieve file content
    file_content = ''
    if user_message.message_type == 'document' and user_message.media_content:
        file_content = f'The student has attached this document to be used as a basis for the study guide: {user_message.media_content}'
        print(file_content)

    system_message = f'''
        Create a self-paced study guide for a specific topic that strictly follows this format:

        <STUDY_GUIDE>

        ## Big Picture
        - Topic:
        - Time Needed:
        - What You Should Already Know:

        💡 Need more detail? Ask me:
        [List of questions to ask for deeper understanding]

        ## Key Questions (3-5)
        [If you can answer these, you understand the topic]

        💡 Want to explore deeper? Ask me:
        [List of questions to ask for deeper understanding]

        ## Must-Know Terms
        [List of terms grouped by key question]

        💡 Stuck on terms? Ask me:
        [List of questions to ask for deeper understanding]

        ## How to Practice
        [List of quick Win Activities]

        [List of deep Understanding Activities]

        💡 Need practice guidance? Ask me:
        [List of questions to ask for deeper understanding]

        ## Study Resources
        ### Main Materials:
        ### Practice Tools:
        ### Extra Help:

        💡 Want to optimize your study? Ask me:
        [List of questions to ask for deeper understanding]

        ## Track Your Progress
        [List of checkpoints to determine when you can explain each key question confidently]

        💡 Unsure about your progress? Ask me:
       [List of questions to ask for deeper understanding]

        ## Tips for Success
        - Common Hangups:
        - Smart Strategies:
        - Time-Saving Tips:

        💡 Looking for personalized advice? Ask me:
        [List of questions to ask for deeper understanding]

        ## Follow-Up Prompts
        [List of questions to ask me while and after studying]

        </STUDY_GUIDE>

        # IMPORTANT
        - Present content directly without tags, hints or technical elements
        - Use clear, standard formatting and headings throughout
        - Write in the same language as the user's message
        - Include only educational content relevant to the study topic
        - Maintain consistent structure between sections

        # STUDY GUIDE TOPIC
        {user_message.text}
        {context_text}
        {context_content}
        {relevant_memories}
        {file_content}
        {user_profile}
    '''

    model = text_model
    content = [{'type': 'text', 'text': system_message}]

    if user_message.media_content and user_message.message_type == 'image':
        model = image_model
        content.insert(0, {'type': 'image_url', 'image_url': {'url': f'data:image/jpeg;base64,{user_message.media_content}'}})

    response = openai_client.chat.completions.create(model=model, messages=[{'role': 'system', 'content': content}])

    print('TOTAL GUIDE TOKENS')
    user_message.tokens += response.usage.total_tokens
    print(user_message.tokens)

    return response.choices[0].message.content





