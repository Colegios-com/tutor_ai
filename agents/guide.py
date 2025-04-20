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

    # Retrieve previous messages if no context is provided  
    if not user_message.context:
        previous_messages = get_data(f'users/{user_message.phone_number}/messages', order_by='timestamp', limit=20)
        if previous_messages:
            for _, previous_message_data in previous_messages.items():
                parts = []
                previous_message_text = previous_message_data['text']
                parts.append(types.Part.from_text(text=previous_message_text))
                if previous_message_data['message_type'] == 'document' and previous_message_data['media_url']:
                    previous_message_content = f'The accompanying document is attached to the last message you sent me.'
                    parts.append(types.Part.from_text(text=previous_message_content))
                    file = download_file(previous_message_data['media_url'])
                    parts.append(types.Part.from_bytes(data=file, mime_type=previous_message_data['media_mime_type']))
                elif previous_message_data['message_type'] == 'image' and previous_message_data['media_url']:
                    previous_message_content = f'The accompanying image is attached to the last message you sent me.'
                    parts.append(types.Part.from_text(text=previous_message_content))
                    file = download_file(previous_message_data['media_url'])
                    parts.append(types.Part.from_bytes(data=file, mime_type=previous_message_data['media_mime_type']))
                elif previous_message_data['message_type'] == 'video' and previous_message_data['media_url']:
                    previous_message_content = f'The accompanying video is attached to the last message you sent me.'
                    parts.append(types.Part.from_text(text=previous_message_content))
                    file = download_file(previous_message_data['media_url'])
                    parts.append(types.Part.from_bytes(data=file, mime_type=previous_message_data['media_mime_type']))
                
                role = 'user' if previous_message_data['sender'] == 'user' else 'model'
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
        You are a study guide generator specialized in creating structured learning paths designed to complement the **Aldous** tutoring agent. You will generate a comprehensive study guide based on the provided topic, organizing content according to evidence-based pedagogy (chunking, scaffolding, active recall, metacognition) to support Aldous's interactive learning sequence. Your response must be strictly in the specified JSON format with no additional text.

        # REQUIREMENTS

        **Companion Tool:** Generate a guide that serves as a structural foundation for an Aldous tutoring session. It should provide the "map" and key content points Aldous will use interactively.
        **Language:** The study guide must be in the same language as the user's message and provided topic.
        **Fixed Structure:** Generate a study guide with **exactly three levels**:
        - **Level 0:** One main `Module` node.
        - **Level 1:** Exactly **3** `Topic` nodes branching from the Module.
        - **Level 2:** Exactly **3** `Concept` nodes branching from *each* Topic node. Level 2 nodes are leaf nodes and **must not** contain a `branches` key.
        
        **Node Types:** Use `type` values: "Module", "Topic", "Concept".
        
        **Aldous Alignment - Content & Pedagogy:**
        - **Chunking:** The 1 -> 3 -> 3 structure implements chunking. Ensure `description` fields are concise and focused for each chunk.
        - **Logical Progression & Scaffolding:** Content within `description` and the sequence of Topics/Concepts must flow logically (simple to complex). `prerequisites` must clearly link dependent nodes (use `title` for referencing).
        - **Objective Clarity:** `milestone` objects at each level must define clear, measurable outcomes (`criteria`) aligned with Bloom's Taxonomy (moving from recall/understanding at Concept level towards application/analysis at Topic/Module level). The `description` should state the objective simply.
        - **Activation & Context:** Each `Topic` and `Concept` `description` should briefly include context, a real-world link, or an analogy to activate prior knowledge and establish relevance (supporting Aldous's Phase 5).
        - **Socratic & Active Recall Prompts:** `key_questions` must contain primarily Socratic questions that prompt recall, explanation, application, and self-assessment, rather than simple factual checks (supporting Aldous's Phases 6, 7, 8).
        - **Metacognitive Prompts:** Integrate metacognitive questions within `key_questions` (e.g., "How does this connect to [previous concept]?", "What makes this concept challenging?", "How confident are you in applying this? (1-5)", "How would you explain this differently?"). This supports Aldous's Phase 9.
        **Session Planning:** While not a strict JSON field, ensure the *scope* of the content across the 1 Module -> 5 Topics -> 15 Concepts is realistically coverable within 1-3 one-hour Aldous sessions. Topic nodes represent good natural break points.

        # NOTES

        **Aldous's Role:** Remember, Aldous *uses* this guide. The guide provides the structure, explanations, key questions, and milestones; Aldous handles the dynamic interaction, feedback, adaptation, and timing.
        **Descriptions:** Should be clear, concise explanations suitable for Aldous to present or for a student to review (supporting Aldous's Phase 6). Include analogies or brief context where helpful.
        **Key Questions:** Focus on depth. Ask "why," "how," "what if," "compare," "contrast," and self-reflection questions. These are prompts *for* Aldous to ask or for the student to consider.
        **Milestones:** Make `criteria` specific and observable. `measurement` should suggest how Aldous might assess this (e.g., "Verbal explanation", "Problem-solving attempt", "Application to new scenario").
        **Prerequisites:** Essential for Aldous's dependency checking (Phase 3). Be specific, referencing the `title` of prerequisite nodes within the guide.
        **Tone:** Descriptions should adopt a mildly encouraging and clear tone, consistent with Aldous's persona, normalizing potential difficulties.

        # STRUCTURE (Fixed 3 Levels: 1 Module -> 3 Topics -> 3 Concepts each)
    '''

    response = google_client.models.generate_content(
        model='gemini-2.0-flash',
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.3,
            response_mime_type='application/json',
            response_schema = {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "type": {"type": "string"},
                    "description": {"type": "string"},
                    "milestone": {
                        "type": "object",
                        "properties": {
                            "description": {"type": "string"},
                            "criteria": {"type": "array", "items": {"type": "string"}},
                            "measurement": {"type": "string"}
                        },
                        "required": ["description", "criteria", "measurement"]
                    },
                    "prerequisites": {"type": "array", "items": {"type": "string"}},
                    "key_questions": {"type": "array", "items": {"type": "string"}},
                    "branches": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "type": {"type": "string"},
                                "description": {"type": "string"},
                                "milestone": {
                                    "type": "object",
                                    "properties": {
                                        "description": {"type": "string"},
                                        "criteria": {"type": "array", "items": {"type": "string"}},
                                        "measurement": {"type": "string"}
                                    },
                                    "required": ["description", "criteria", "measurement"]
                                },
                                "prerequisites": {"type": "array", "items": {"type": "string"}},
                                "key_questions": {"type": "array", "items": {"type": "string"}},
                                "branches": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "title": {"type": "string"},
                                            "type": {"type": "string"},
                                            "description": {"type": "string"},
                                            "milestone": {
                                                "type": "object",
                                                "properties": {
                                                    "description": {"type": "string"},
                                                    "criteria": {"type": "array", "items": {"type": "string"}},
                                                    "measurement": {"type": "string"}
                                                },
                                                "required": ["description", "criteria", "measurement"]
                                            },
                                            "prerequisites": {"type": "array", "items": {"type": "string"}},
                                            "key_questions": {"type": "array", "items": {"type": "string"}}
                                        },
                                        "required": ["title", "type", "description", "milestone", "prerequisites", "key_questions"]
                                    }
                                }
                            },
                            "required": ["title", "type", "description", "milestone", "prerequisites", "key_questions", "branches"]
                        }
                    }
                },
                "required": ["title", "type", "description", "milestone", "prerequisites", "key_questions", "branches"]
            }
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
