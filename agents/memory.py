from init.google_ai import google_client
from google.genai import types

from utilities.account import update_usage
from storage.embedding import embed_data
from storage.storage import save_data, download_file
from storage.vector_storage import query_vectors, save_vectors

from data.models import Message

import base64

def initialize_memory_workflow(user_message: Message, response_message: Message) -> str:    
    contents = []
    # Retrieve relevant memories
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
    elif user_message.message_type == 'document':
        file = download_file(user_message.media_url)
        parts.append(types.Part.from_bytes(data=file, mime_type=user_message.media_mime_type))

    contents.append(types.Content(parts=parts, role='user'))

    
    system_prompt = f'''
        # Purpose: Generate concise summaries of student interactions optimized for vector similarity search.

        ## Process:
        1. **Analyze Interaction:** Identify the main topic, key concepts discussed, any challenges the student faced, and any solutions or explanations provided.
        2. **Synthesize Summary:** Create a short, declarative summary that captures the core meaning of the interaction. The summary should:
            *   Focus on the *underlying concepts* rather than specific problem details.
            *   Use precise and unambiguous language.
            *   Highlight relationships to other potential topics.
            *   Include keywords that are relevant to the domain.
        3. **Tag Related Concepts:** Explicitly list related concepts that could be relevant for future searches.

        ## Format:
        SUMMARY: [Concise summary of the interaction]
        RELATED_CONCEPTS: [Comma-separated list of related concepts]

        ## Rules:
        *   Keep the summary concise (ideally under 50 words).
        *   Use keywords that are specific and relevant to the domain.
        *   Focus on the conceptual understanding, not just the procedural steps.
        *   Avoid jargon or overly technical language.
        *   Prioritize clarity and accuracy.
        *   Generate *multiple* `RELATED_CONCEPTS` tags to capture various associations.

        ## Examples:

        **Example 1 (Geometry - Cube and Square - Challenge):**
        SUMMARY: Student struggled with calculating the surface area of a cube. Explanation focused on understanding that a cube's surface area is the sum of the areas of its six square faces.
        RELATED_CONCEPTS: Area of squares, Surface area, 3D geometry, Geometric shapes, Area calculation, Perimeter, Volume

        **Example 2 (History - The French Revolution - Challenge):**
        SUMMARY: Student struggled to connect the economic conditions in pre-revolutionary France with the rise of popular discontent. The explanation emphasized the impact of famine, taxation, and inequality on the Third Estate.
        RELATED_CONCEPTS: French Revolution, Estates-General, Louis XVI, Marie Antoinette, Inequality, Taxation, Enlightenment, Social unrest, Political revolution

        **Example 3 (Music Theory - Chord Progressions - Understanding):**
        SUMMARY: Student correctly identified and analyzed several common chord progressions in a major key, demonstrating a solid grasp of diatonic harmony.
        RELATED_CONCEPTS: Chord progressions, Music theory, Harmony, Diatonic chords, Key signatures, Musical analysis, Composition
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

    update_usage(user_message)

    memory = response.text

    embeddings = embed_data([memory])
    metadata = {'user': user_message.phone_number, 'context_type': 'general'}

    if user_message.media_id:
        metadata['media_id'] = user_message.media_id

    save_vectors(metadata=metadata, data=[memory], embeddings=embeddings)

    last_interaction_url = f'users/{user_message.phone_number}/last_interaction'
    message_url = f'users/{user_message.phone_number}/messages/{user_message.id.replace('wamid.', '')}'
    response_url = f'users/{user_message.phone_number}/messages/{response_message.id.replace('wamid.', '')}'
    save_data(last_interaction_url, {'timestamp': user_message.timestamp, 'user_message': user_message.dict(), 'response_message': response_message.dict()})
    save_data(message_url, user_message.dict())
    save_data(response_url, response_message.dict())
