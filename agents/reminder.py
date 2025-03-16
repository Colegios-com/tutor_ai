from init.google_ai import google_client
from google.genai import types

from storage.storage import get_data, download_file

from data.models import Message


def initialize_reminder_workflow(user_message: Message) -> str:
    contents = []
    
    previous_messages = get_data(f'users/{user_message.phone_number}/messages', order_by='timestamp', limit=10)
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


    system_prompt = f'''
        You are an engaging educational reminder system. Your goal is to analyze recent student interactions and craft a personalized, motivating reminder that will encourage continued learning engagement.

        # REQUIREMENTS
        1. Analyze the conversation history to identify:
           - Main topics of interest
           - Learning patterns
           - Areas of struggle or success
           - Incomplete topics or discussions
           - Level of engagement

        2. Craft a reminder that:
           - Is personal and friendly
           - References specific topics from their learning history
           - Provides a clear call to action
           - Includes an interesting fact or hook related to their interests
           - Suggests a next step in their learning journey

        3. Reminder Structure:
           - Greeting (use their name if available)
           - Personal connection to their recent learning
           - Interesting fact or insight
           - Specific suggestion for next learning step
           - Encouraging closing note

        # TONE AND STYLE
        - Be encouraging but not pushy
        - Show awareness of their learning journey
        - Be specific rather than generic
        - Use natural, conversational language
        - Include emojis appropriately (1-2 maximum)
        - Keep it concise (100-150 words maximum)
        - Respond in the same language as the user's last messages
    '''

    user_prompt = f'''
        Please analyze these recent interactions and craft an engaging reminder for this student. The last message was sent less that 24 hours ago.
    '''

    contents.append(types.Part.from_text(text=user_prompt))

    response = google_client.models.generate_content(
        model='gemini-2.0-flash',
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.7,
        ),
    )

    # Extract components for WhatsApp template
    reminder_text = response.text

    return reminder_text 