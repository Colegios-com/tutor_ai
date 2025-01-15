from init.openai import openai_client

from utilities.parsing import repair_json
from utilities.storage import save_data, get_data
from utilities.vector_storage import query_vectors

from data.models import Message

import json
import uuid


# image_model = 'accounts/fireworks/models/llama-v3p2-90b-vision-instruct'
# text_model = 'accounts/fireworks/models/llama-v3p3-70b-instruct'
image_model = 'accounts/fireworks/models/qwen2-vl-72b-instruct'
text_model = 'accounts/fireworks/models/qwen2p5-72b-instruct'


def initialize_guide_workflow(user_message: Message) -> str:
    # Retrieve user profile information
    user_profile = ''
    user_profile_data = get_data(f'users/{user_message.phone_number}/profile')
    if user_profile_data:
        user_profile = f'This is my academic profile: {user_profile_data}'
        print(user_profile)

    # Retrieve context information
    context_text = ''
    context_content = ''
    context_image = ''
    if user_message.context:
        context_data = get_data(f'users/{user_message.phone_number}/messages/{user_message.context.replace("wamid.", "")}')
        if context_data:
            context_text = f'Use this message as a reference when creating my study guide: {context_data['text']}'
            print(context_text)
            if context_data['message_type'] == 'document' and context_data['media_content']:
                context_content = f'This document is attached to the reference message: {context_data['media_content']}'
                print(context_content)
            elif context_data['message_type'] == 'image' and context_data['media_content']:
                context_content = f'The accompanying image is attached to the reference message.'
                context_image = context_data['media_content']
                print(context_content)
                print(context_image)

    # Retrieve relevant memories
    relevant_memories = ''
    memories_data = query_vectors(data=user_message.text, user=user_message.phone_number)
    if memories_data:
        relevant_memories = f'These memories are relevant to the creation of my study guide: {memories_data}'
        print(relevant_memories)

    # Retrieve file content
    file_content = ''
    if user_message.message_type == 'document' and user_message.media_content:
        file_content = f'Use this document in the creation of my study guide: {user_message.media_content}'
        print(file_content)

    system_prompt = f'''
        You are a study guide generator specialized in creating structured learning paths. You will generate a comprehensive study guide based on the provided topic, organizing content from fundamental concepts to advanced mastery. Your response must be strictly in the specified JSON format with no additional text.

        # REQUIREMENTS
        - Generate a recursive tree structure where each node can branch into multiple sub-topics
        - Each node must specify its type
        - Include clear, measurable milestones for each learning component
        - Ensure logical progression of concepts
        - Include prerequisites and key questions for each node
        - Each branch should represent a distinct learning path or sub-topic
        - Leaf nodes should contain specific, actionable learning points

        # STRUCTURE
        {{"title": "[main topic or subject area]", "type": "[type of subject area]", "description": "[comprehensive overview of this learning node]", "milestone": {{"description": "[what success looks like for this node]", "criteria": [list of specific measurable outcomes], "measurement": "[how to assess achievement of criteria]"}}, "prerequisites": [list of required knowledge and/or skills], "key_questions": [list of key questions the student can ask you to strengthen their learning], "branches": [{{"title": "[sub-topic or component]", "type": "[type of sub-topic or component]", "description": "[detailed explanation of this branch]", "milestone": {{"description": "[specific success criteria for this branch]", "criteria": [list of branch specific outcomes], "measurement": "[branch-specific assessment method]"}}, "prerequisites": [list of branch specific requirements], "key_questions": [list of branch specific key questions the user can ask you to strengthen their learning], "branches": [{{"title": "[further subtopic]", "type": "[type of subtopic]", "description": "[specific concept details]", "milestone": {{"description": "[detailed success criteria]", "criteria": [list of detailed outcomes], "measurement": "[specific assessment method]"}}, "prerequisites": [list of specific requirements], "key_questions": [list of specific questions the user can ask you to strengthen their learning], "branches": []}}]}}]}}

        # NOTES
        - Each branch should represent a logical subdivision of the parent topic
        - Milestones should become more specific as you move deeper into the tree
        - Key question lists should be relevant to the specific node's content
        - Prerequisites should clearly indicate what's needed before starting that node
    '''

    user_prompt = f'''
        # EVALUATION TOPIC
        {user_message.text}
        {context_text}
        {context_content}
        {relevant_memories}
        {file_content}
        {user_profile}
    '''

    model = text_model
    system_content = [{'type': 'text', 'text': system_prompt}]
    user_content = [{'type': 'text', 'text': user_prompt}]

    if user_message.media_content and user_message.message_type == 'image':
        model = image_model
        user_content.insert(0, {'type': 'image_url', 'image_url': {'url': f'data:image/jpeg;base64,{user_message.media_content}'}})

    response = openai_client.chat.completions.create(model=model, messages=[{'role': 'system', 'content': system_content}, {'role': 'user', 'content': user_content}])

    print('TOTAL GUIDE TOKENS')
    user_message.tokens += response.usage.total_tokens
    print(user_message.tokens)

    guide_id = str(uuid.uuid4())
    guide_url = f'users/{user_message.phone_number}/guides/{guide_id}'
    raw_guide = response.choices[0].message.content
    repaired_guide = repair_json(raw_guide)
    guide = json.loads(repaired_guide)

    print(repaired_guide)

    save_data(guide_url, guide)

    return guide_id





