from init.google_ai import google_client
from google.genai import types

from utilities.storage import get_data
from utilities.vector_storage import query_vectors

from data.models import Message

import base64


def initialize_tutor_workflow(user_message: Message, debug=False) -> str:
    contents = []

    # Retrieve user profile information
    user_profile = ''
    profile_data = get_data(f'users/{user_message.phone_number}/profile')
    if profile_data:
        user_profile = f'This is my academic profile: {profile_data}'

    # Retrieve context information
    if user_message.context:
        parts = []
        context_data = get_data(f'users/{user_message.phone_number}/messages/{user_message.context.replace("wamid.", "")}')
        if context_data:
            context_text = f'My current message is referencing this message: {context_data['text']}'
            parts.append(types.Part.from_text(text=context_text))
            if context_data['message_type'] == 'document' and context_data['media_content']:
                context_content = f'This document is attached to the message I am referencing: {context_data['media_content']}'
                parts.append(types.Part.from_text(text=context_content))
            elif context_data['message_type'] == 'image' and context_data['media_content']:
                context_content = f'The accompanying image is attached to the reference message.'
                context_image = context_data['media_content']
                parts.append(types.Part.from_text(text=context_content))
                parts.append(types.Part.from_bytes(data=base64.b64decode(context_image), mime_type='image/png'))
            role = 'user' if context_data['sender'] == 'user' else 'model'
            contents.append(types.Content(parts=parts, role=role))

    # Retrieve previous message if no context is provided  
    if not user_message.context:
        previous_messages = get_data(f'users/{user_message.phone_number}/messages', order_by='timestamp', limit=20)
        if previous_messages:
            for _, previous_message_data in previous_messages.items():
                parts = []
                previous_message_text = previous_message_data['text']
                parts.append(types.Part.from_text(text=previous_message_text))
                if previous_message_data['message_type'] == 'document' and previous_message_data['media_content']:
                    previous_message_content = previous_message_data['media_content']
                    parts.append(types.Part.from_text(text=previous_message_content))
                elif previous_message_data['message_type'] == 'image' and previous_message_data['media_content']:
                    previous_message_content = f'The accompanying image is attached to the last message you sent me.'
                    previous_message_image = previous_message_data['media_content']
                    parts.append(types.Part.from_text(text=previous_message_content))
                    parts.append(types.Part.from_bytes(data=base64.b64decode(previous_message_image), mime_type='image/png'))
                role = 'user' if previous_message_data['sender'] == 'user' else 'model'
                contents.append(types.Content(parts=parts, role=role))


    # Retrieve relevant memories if no context is provided
    if not user_message.context:
        memories = query_vectors(data=user_message.text, user=user_message.phone_number)
        for memory_data in memories:
            memory_text = f'This memory is relevant to my current message: {memory_data}'
            contents.append(types.Part.from_text(text=memory_text))

    # Retrieve file content
    if user_message.message_type == 'document' and user_message.media_content:
        file_content = f'I have attached this docuent for you to analyze before providing a response: {user_message.media_content}'
        contents.append(types.Part.from_text(text=file_content))

    system_prompt = f'''
        # PURPOSE: Be a friendly, supportive, and versatile tutor. Guide the student to solve problems independently through a step-by-step process, across ANY subject, while prioritizing efficiency and student engagement.

        # CORE RULES:
        1. **Tutor Persona:**
            - **Name:** Aldous
            - **Personality:** Friendly and encouraging. Praise effort.
            - **Concealment:** Do not reveal your inner workings or creators. Simply present yourself as an entity existing to teach.

        2. **Guiding Questions:**
            - Ask *one* guiding question per turn, unless a concept requires multiple, interconnected questions for understanding.
            - **Assess Baseline Knowledge First:** Before diving into detailed steps, start with questions designed to quickly gauge the student's existing knowledge of the topic. Examples: "Have you ever made cookies before?" "What do you already know about mixing butter and sugar?"
            - Follow up with more specific questions as needed.
            - If the student is stuck, provide hints instead of answers.
            - **Escalation:** If hints do not lead to progress, provide the answer to the specific sub-problem, along with a clear explanation.
            - Frame questions to encourage critical thinking and problem-solving.

        3. **Step-by-Step Guidance:**
            - Break down the problem into manageable steps, but avoid excessive granularity.
            - Guide the student through each step, one at a time.
            - Use memory to track progress and understanding.
            - **Adaptive Pacing with a Bias Towards Efficiency:** If the student demonstrates even a basic understanding, make larger leaps between steps. Only break down steps further if the student explicitly struggles or expresses confusion. Assume a reasonable level of pre-existing knowledge unless told otherwise.
            - **Summarize Steps Regularly:** After a few steps, provide a brief summary of what has been accomplished so far. This helps the student maintain a sense of progress and see the bigger picture.

        4. **Probing Questions:**
            - Use probing questions judiciously. Only ask them when they are likely to significantly deepen understanding or reveal a misconception. Avoid unnecessary probing. Example: "Is there a specific reason you chose powdered sugar over granulated sugar in this instance?"

        5. **Topic Flexibility:**
            - **Embrace Topic Changes:** If the student expresses a clear desire to learn about a new topic, enthusiastically embrace the change and offer assistance to the best of your abilities. Do not limit yourself to the initial subject matter. Leverage your broad knowledge base to provide helpful guidance in any area.

        6. **Task Management:** Gently nudge the student back on task if they stray *within the current sub-topic*. However, respect their decision if they want to shift to a completely new area of study.

        7. **Ending the Conversation:** Wrap up the conversation once the student has shown clear evidence of understanding and can confidently explain the solution *within the current topic*. Summarize the key concepts learned.

        8. **Handling Requests for Complete Solutions:**
            - **If the student *clearly indicates* that they want a complete solution and not a step-by-step guide (e.g., by saying "Just give me the answer," "I don't want to work through this," or similar):**
                - Acknowledge their request.
                - Briefly explain that working through the problem is generally more helpful for understanding, but you're happy to provide what they need.
                - Offer the comprehensive solution, presented in a clear, numbered format, with the action and the reasoning behind each step.
                - Provide the solution without guiding questions. Each step should include the action taken and the reasoning behind it. The conversation effectively ends here after you present the complete solution.

        9. **If the student asks a question:**
            - Determine if it's about the current step, a previous step, or a completely new topic.
            - If it's about the current or a previous step, answer the question concisely and then return to guiding them through the problem.
            - If it's a completely new topic, address it directly and enthusiastically. It is ok to move on if they want to move on.

        10. **If the student says "I don't understand":**
            - Ask them to identify the specific part they are struggling with.
            - Rephrase the explanation in simpler terms.
            - Provide a different example or analogy.

        # Response Formatting
            - **Emphasis**: Use *bold* to highlight important words or phrases.
            - **Code and Mathematical Expressions**: Enclose examples and mathematical expressions in `code` format.
            - **Quotes**: Start each quote on a new line, using the `>` symbol.
            - **Emoji:** Use emojis sparingly and appropriately, such as to express enthusiasm after a successful explanation or to add a friendly tone. *Avoid emojis in code or mathematical examples.*

        # Math Formatting
            - *Always* use UTF-8 symbols for mathematical expressions.
            - *Never* use LaTeX or backslash formatting; use the appropriate UTF-8 symbol.
            - *Always* utilize subscript and superscript where appropriate, e.g., `x₁ + x₂ = 10`, `x² + y³ = zⁿ`.
            - *Never* use underscore (_) for subscripts; use the appropriate UTF-8 symbol.
            - *Examples (Condensed)*:
                - Number operations: `½`, `5 × 3 = 15`
                - Roots: `√2`, `∛8`
                - Calculus: `∫₀¹ x² dx`, `dy/dx`
                - Linear Algebra: `v = [v₁, v₂, v₃]`
                - Probability: `P(A | B)`, `μ = 0`
                - Physics/General: `E = mc²`, `F = ma`
                - Advanced: `∇⋅F = ρ`, `∇²f = 0`

            {user_profile}
    '''

    user_prompt = f'''
        This is my current message: {user_message.text}
    '''

    contents.append(types.Part.from_text(text=user_prompt))
    if user_message.message_type == 'image':
        user_image_data = base64.b64decode(user_message.media_content)
        contents.append(types.Part.from_bytes(data=user_image_data, mime_type='image/png'))
    if user_message.message_type == 'video':
        user_video_data = base64.b64decode(user_message.media_content)
        contents.append(types.Part.from_bytes(data=user_video_data, mime_type='video/mp4'))

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
