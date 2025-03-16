from init.google_ai import google_client
from google.genai import types

from utilities.parsing import repair_json
from storage.storage import save_data, get_data, download_file
from storage.vector_storage import query_vectors

from data.models import Message

import base64
import json
import uuid


def initialize_guide_workflow(user_message: Message) -> str:
    contents = []

    # Get user profile for context
    profile_data = get_data(f'users/{user_message.phone_number}/profile')
    if profile_data:
        profile_text = f'Student Profile: {profile_data}'
        contents.append(types.Part.from_text(text=profile_text))

    # Retrieve context information
    if user_message.context:
        parts = []
        context_data = get_data(f'users/{user_message.phone_number}/messages/{user_message.context.replace("wamid.", "")}')
        if context_data:
            context_text = f'My current message is referencing this message: {context_data['text']}'
            parts.append(types.Part.from_text(text=context_text))
            if context_data['message_type'] == 'document':
                context_content = f'The accompanying document is attached to the reference message.'
                parts.append(types.Part.from_text(text=context_content))
                file = download_file(context_data['media_url'])
                parts.append(types.Part.from_bytes(data=file, mime_type=context_data['media_mime_type']))
            elif context_data['message_type'] == 'image':
                context_content = f'The accompanying image is attached to the reference message.'
                parts.append(types.Part.from_text(text=context_content))
                file = download_file(context_data['media_url'])
                parts.append(types.Part.from_bytes(data=file, mime_type=context_data['media_mime_type']))
            elif context_data['message_type'] == 'video':
                context_content = f'The accompanying video is attached to the reference message.'
                parts.append(types.Part.from_text(text=context_content))
                file = download_file(context_data['media_url'])
                parts.append(types.Part.from_bytes(data=file, mime_type=context_data['media_mime_type']))
            role = 'user' if context_data['sender'] == 'user' else 'model'
            contents.append(types.Content(parts=parts, role=role))

    # Retrieve relevant memories if no context is provided
    if not user_message.context:
        memories = query_vectors(data=user_message.text, user=user_message.phone_number)
        for memory_data in memories:
            memory_text = f'This memory is relevant to my current message: {memory_data}'
            contents.append(types.Part.from_text(text=memory_text))

    user_prompt = f'''
        This is my current message: {user_message.text}
    '''

    parts = []
    parts.append(types.Part.from_text(text=user_prompt))

    if user_message.message_type == 'image':
        file = download_file(user_message.media_url)
        parts.append(types.Part.from_bytes(data=file, mime_type=user_message.media_mime_type))

    elif user_message.message_type == 'video':
        file = download_file(user_message.media_url)
        parts.append(types.Part.from_bytes(data=file, mime_type=user_message.media_mime_type))
    # Retrieve file content
    elif user_message.message_type == 'document':
        file = download_file(user_message.media_url)
        parts.append(types.Part.from_bytes(data=file, mime_type=user_message.media_mime_type))
    
    contents.append(types.Content(parts=parts, role='user'))

    system_prompt = f'''
        You are a study guide generator specialized in creating structured learning paths. You will generate a comprehensive study guide based on the provided topic, organizing content from fundamental concepts to advanced mastery. Your response must be strictly in the specified JSON format with no additional text.

        # REQUIREMENTS
        - The study guide must be in the same language as the user's message and provided context
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

    guide_id = str(uuid.uuid4())
    guide_url = f'users/{user_message.phone_number}/guides/{guide_id}'
    raw_guide = response.text
    repaired_guide = repair_json(raw_guide)
    guide = json.loads(repaired_guide)

    save_data(guide_url, guide)

    return guide_id
