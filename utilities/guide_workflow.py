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
        Create a personalized study guide for a specific topic. The guide should be structured as a learning pathway, with the following sections:

        ## Introduction to the Learning Pathway
        * Topic: [Topic]
        * Time Needed: [estimated time required to complete the pathway]
        * What You Should Already Know: [prerequisites for the topic]

        ## Core Objectives
        * List 3-5 core objectives that I should focus on to master the topic
        * For each objective, provide:
            + A brief explanation of the concept
            + Examples or illustrations to help clarify the concept
            + Suggestions for how to practice and reinforce my understanding
        * Optional Side Quests:
            + List additional activities or topics that I can explore to gain extra knowledge or skills
            + Provide suggestions for how to incorporate these side quests into my learning pathway

        ## Essential Terms and Concepts
        * List essential terms and concepts, grouped by core objective
        * Provide definitions, explanations, and examples for each term or concept
        * Suggest ways to practice and reinforce my understanding of each term or concept
        * Bonus Materials:
            + List additional resources or activities that I can use to deepen my understanding of the topic
            + Provide suggestions for how to use these bonus materials to support my learning

        ## Study Resources and Tools
        * List recommended study resources, including:
            + Main materials (e.g. textbooks, articles, videos)
            + Practice tools (e.g. quizzes, worksheets, interactive simulations)
            + Extra help (e.g. online forums, tutoring services)
        * Provide suggestions for how to use each resource to support my learning
        * Power-Ups:
            + List additional tools or resources that I can use to accelerate my learning or overcome challenges
            + Provide suggestions for how to use these power-ups to support my learning

        ## Tracking Progress and Staying on Track
        * Provide a progress tracking system, with checkpoints to determine when I can explain each core objective confidently
        * Offer tips for staying motivated and on track, including:
            + Common hangups and how to overcome them
            + Smart strategies for managing time and effort
            + Time-saving tips and shortcuts
        * Leveling Up:
            + Provide suggestions for how to reflect on my progress and adjust my learning pathway as needed
            + Offer tips for how to celebrate my successes and stay motivated

        ## Deepening Understanding and Exploring Further
        * For each section, provide suggestions for questions I can ask to:
            + Deepen my understanding of the topic
            + Clarify doubts or misconceptions
            + Explore related topics or applications
        * Encourage me to ask questions and seek guidance throughout my journey
        * Hidden Gems:
            + List additional topics or activities that I can explore to gain a deeper understanding of the subject
            + Provide suggestions for how to incorporate these hidden gems into my learning pathway

        ## Final Checkpoints and Next Steps
        * Provide a final set of checkpoints to ensure I have mastered the core objectives and concepts
        * Offer suggestions for next steps, including:
            + How to apply my new knowledge and skills
            + How to continue learning and exploring the topic
            + How to seek feedback and assessment from others
        * Graduation:
            + Provide a final assessment of my progress and mastery of the topic
            + Offer suggestions for how to celebrate my achievements and reflect on my learning journey

        Please generate the study guide in a standard format, with clear headings and concise language, and adapt the content to match my language and profile. Use only educational content relevant to the study topic, and avoid technical jargon or unnecessary complexity.
        Note: Please ensure that all headings and section titles are translated to match the language of my request, and that the content is tailored to my specific needs and learning style. The output token count must remain under 3000 tokens.
        
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

    response = openai_client.chat.completions.create(model=model, messages=[{'role': 'system', 'content': content}], max_tokens=3000)

    print('TOTAL GUIDE TOKENS')
    user_message.tokens += response.usage.total_tokens
    print(user_message.tokens)

    return response.choices[0].message.content





