# Init
from init.whatsapp import whatsapp_client

from data.models import Message
from typing import Optional
from utilities.document_parser import parse_document
from storage.storage import get_data, upload_file
import uuid

# Standard
import time
from datetime import datetime, timedelta


def verify_message_payload(payload: dict) -> bool:
    try:
        payload['entry'][0]['changes'][0]['value']['messages']
        return True
    except (KeyError, TypeError, IndexError):
        return False


def is_duplicate_message(payload: dict) -> bool:
    phone_number = payload['entry'][0]['changes'][0]['value']['messages'][0]['from']
    message_id = payload['entry'][0]['changes'][0]['value']['messages'][0]['id']
    url = f'users/{phone_number}/messages'
    messages = get_data(url)
    if messages:
        return any(value['id'] == message_id for value in messages.values())
    return False


def extract_base_data(payload: dict) -> dict:
    try:
        message_data = payload['entry'][0]['changes'][0]['value']['messages'][0]
        base_data = {
            'id': message_data['id'],
            'phone_number_id': payload['entry'][0]['changes'][0]['value']['metadata']['phone_number_id'],
            'sender': 'user',
            'phone_number': message_data['from'],
            'timestamp': time.time(),
        }
        if 'context' in message_data:
            if 'id' in message_data['context']:
                base_data['context'] = message_data['context']['id']
        return base_data
    except KeyError as e:
        raise ValueError(f"Missing key in payload: {e}")
    except IndexError:
        raise ValueError("Invalid payload structure.")


def parse_text_message(message: dict) -> tuple[str, str]:
    body = message['text']['body']
    if body.startswith(('/perfil', '/analisis', '/guia', '/imagen', '/examen')):
        message_type, _, text = body.partition(' ')
    else:
        message_type = 'text'
        text = body
    return message_type, text


def process_media_message(message: dict, message_type: str) -> tuple[str, Optional[str], Optional[str]]:
    try:
        media_id = message[message_type]['id']
        media_url, media_mime_type = whatsapp_client.get_media_url(id=media_id)
        file = whatsapp_client.download_media(url=media_url)

        media_type, media_extension = media_mime_type.split('/')
        media_url = upload_file(file, file_path=f'{message.get('from')}/{media_type}/{media_id}.{media_extension}')
        text = get_media_message_text(message, file, message_type)

        return text, media_id, media_url, media_mime_type
    except Exception as e:
        print(f"Error processing media message: {e}")
        raise ValueError("Error processing media message.")


def get_media_message_text(message:dict, file: bytes, message_type:str) -> str:
    if message_type == 'audio':
        text = whatsapp_client.transcribe_audio(file=file)
    elif message_type == 'document':
        file_type = message['document']['mime_type']
        text = parse_document(data=file, file_type=file_type)
    else:
        text = message[message_type].get('caption', f'User sent {message_type}. Build your response based on the {message_type} and the conversation history. Respond in the same language the user has been using in the conversation.')

    return text


def build_user_message(payload: dict) -> Message:
    try:
        base_data = extract_base_data(payload)
        message = payload['entry'][0]['changes'][0]['value']['messages'][0]
        message_type = message.get('type')

        if message_type == 'text':
            message_type, text = parse_text_message(message)
            return Message(
                **base_data,
                message_type=message_type,
                text=text,
            )
        elif message_type in ('image', 'video', 'sticker', 'audio', 'document'):
            text, media_id, media_url, media_mime_type = process_media_message(message, message_type)
            return Message(
                **base_data,
                message_type=message_type,
                text=text,
                media_id=media_id,
                media_url=media_url,
                media_mime_type=media_mime_type,
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
        id=f'{user_message.id}-r',
        phone_number_id=user_message.phone_number_id,
        sender='agent',
        phone_number=user_message.phone_number,
        message_type=message_type,
        text=raw_response,
        media_id=media_id,
        timestamp=time.time(),
    )


def build_reminder_message(user_data: dict) -> Message:
    """
    Build a Message object from user's last interaction data for reminder purposes
    """
    last_interaction = user_data.get('last_interaction', {})
    if not last_interaction:
        return None

    user_message = last_interaction.get('user_message', {})
    if not user_message:
        return None

    # Convert dict to Message object if it isn't already
    if isinstance(user_message, dict):
        user_message = Message(**user_message)
    
    return user_message
