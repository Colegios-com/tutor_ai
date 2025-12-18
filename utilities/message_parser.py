# Init
from init.whatsapp import whatsapp_client
from init.google_ai import google_client

from google.genai.types import UploadFileConfig

from data.models import Message, File
from typing import Optional

# Storage
from storage.storage import get_message

# Standard
import tempfile
import os


def verify_message_payload(payload: dict) -> bool:
    try:
        payload['entry'][0]['changes'][0]['value']['messages']
        return True
    except (KeyError, TypeError, IndexError):
        return False


def is_duplicate_message(payload: dict) -> bool:
    whatsapp_message_id = payload['entry'][0]['changes'][0]['value']['messages'][0]['id']
    return get_message(whatsapp_message_id)


def extract_base_data(payload: dict) -> dict:
    try:
        message_data = payload['entry'][0]['changes'][0]['value']['messages'][0]
        base_data = {
            'whatsapp_message_id': message_data['id'],
            'phone_number_id': payload['entry'][0]['changes'][0]['value']['metadata']['phone_number_id'],
            'sender': 'user',
            'wa_id': payload['entry'][0]['changes'][0]['value']['contacts'][0]['wa_id'],
        }
        if 'context' in message_data:
            if 'id' in message_data['context']:
                base_data['context'] = message_data['context']['id']
        return base_data
    except KeyError as e:
        raise ValueError(f"Missing key in payload: {e}")
    except IndexError:
        raise ValueError("Invalid payload structure.")


# Do not worry about now
def process_media_message(message: dict, message_type: str) -> tuple[str, Optional[str], Optional[str]]:
    try:
        media_id = message[message_type]['id']
        media_url, mime_type = whatsapp_client.get_media_url(id=media_id)

        file = whatsapp_client.download_media(url=media_url)

        # Save file to temporary location
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(file)
            temp_file_path = temp_file.name
        try:
            # 2. Upload the file using the closed file's path
            uploaded_file = google_client.files.upload(
                file=temp_file_path, 
                config=UploadFileConfig(mime_type=mime_type)
            )
            return uploaded_file

        finally:
            # 3. Clean up the temporary file manually
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    except Exception as e:
        print(f"Error processing media message: {e}")
        raise ValueError("Error processing media message.")


def build_user_message(payload: dict) -> Message:
    try:
        base_data = extract_base_data(payload)
        message = payload['entry'][0]['changes'][0]['value']['messages'][0]
        message_type = message.get('type')

        if message_type == 'text':
            return Message(
                **base_data,
                message_type='text',
                text=message['text']['body'],
            )
        elif message_type in ('image', 'video', 'sticker', 'audio', 'document'):
            file = process_media_message(message, message_type)
            return Message(
                **base_data,
                message_type=message_type,
                file=File(uri=file.uri, mime_type=file.mime_type),
            )
        else:
            raise ValueError('Unprocessable message type.')

    except Exception as error_message:
        print(f"Error building message: {error_message}")

        message_type = message.get('type', 'unknown')
        text = message.get(message_type, {}).get('caption', 'Unable to retrieve message for message type.') if message else str(error_message)
        base_data = extract_base_data(payload) if 'payload' in locals() else {} #make sure base_data is defined

        return Message(
            **base_data,
            message_type=f'unsupported/{message_type}',
            text=text,
        )


def build_agent_message(user_message: Message, raw_response: str, message_type: str = 'text', media_id: str = None) -> Message:
    """Builds a response Message object based on the user message."""
    return Message(
        whatsapp_message_id=f'{user_message.whatsapp_message_id}',
        phone_number_id=user_message.phone_number_id,
        sender='model',
        wa_id=user_message.wa_id,
        message_type=message_type,
        text=raw_response,
        media_id=media_id,
    )
