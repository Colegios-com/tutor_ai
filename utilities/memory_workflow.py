from init.google_ai import google_client
from google.genai import types

from utilities.embedding import embed_data
from utilities.storage import save_data
from utilities.vector_storage import query_vectors, save_vectors

from data.models import Message

import base64


def initialize_memory_workflow(user_message: Message, response_message: Message) -> str:    
    # Retrieve relevant memories
    relevant_memories = ''
    memories_data = query_vectors(data=user_message.text, user=user_message.phone_number)
    if memories_data:
        relevant_memories = f'These memories are relevant to my latest message: {memories_data}'

    # Retrieve file content
    file_content = ''
    if user_message.message_type == 'document' and user_message.media_content:
        file_content = f'I have attached this docuent for you to analyze before providing a response: {user_message.media_content}'
    
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

    user_prompt = f'''
        This is my latest message: {user_message.text}
        {file_content}
        This is your response to my latest message: {response_message.text}
        {relevant_memories}
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

    memory = response.text

    embeddings = embed_data([memory])
    metadata = {'user': user_message.phone_number, 'context_type': 'general'}

    if user_message.media_id:
        metadata['media_id'] = user_message.media_id

    save_vectors(metadata=metadata, data=[memory], embeddings=embeddings)

    message_url = f'users/{user_message.phone_number}/messages/{user_message.id.replace('wamid.', '')}'
    response_url = f'users/{user_message.phone_number}/messages/{response_message.id.replace('wamid.', '')}'
    save_data(message_url, user_message.dict())
    save_data(response_url, response_message.dict())
