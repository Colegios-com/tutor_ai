
from init.whatsapp import whatsapp_client

from utilities.extract_document_text import DocumentParser
from utilities.storage import get_data

from data.models import Message

from time import time


parser = DocumentParser()

def verify_message(payload: dict) -> bool:
    if 'entry' not in payload:
        return False
    if 'changes' not in payload['entry'][0]:
        return False
    if 'value' not in payload['entry'][0]['changes'][0]:
        return False
    if 'messages' not in payload['entry'][0]['changes'][0]['value']:
        return False
    return True


def check_message(message: Message) -> bool:
    # Object Storage
    url = f'users/{message.phone_number}/messages'
    messages = get_data(url)
    if messages:
        for value in messages.values():
            if value['id'] == message.id:
                return True
    return False


def build_user_message(payload: dict) -> Message:
    try:
        # Build Base Data
        message = payload['entry'][0]['changes'][0]['value']['messages'][0]
        base_data = {
            'id': payload['entry'][0]['changes'][0]['value']['messages'][0]['id'],
            'phone_number_id': payload['entry'][0]['changes'][0]['value']['metadata']['phone_number_id'],
            'sender': 'user',
            'phone_number': payload['entry'][0]['changes'][0]['value']['messages'][0]['from'],
            'timestamp': time(),
        }

        if 'context' in message:
            base_data['context'] = message['context']['id']
        
        # Build Type Specific Data
        if 'text' in message:
            if message['text']['body'].startswith('/perfil'):
                message_type, _, text = message['text']['body'].partition(' ')
            elif message['text']['body'].startswith('/analisis'):
                message_type, _, text = message['text']['body'].partition(' ')
            elif message['text']['body'].startswith('/examen'):
                message_type, _, text = message['text']['body'].partition(' ')
            else:
                message_type = 'text'
                text = message['text']['body']

            return Message(
                **base_data,
                message_type=message_type,
                text=text,
            )
        
        elif 'image' in message:
            media_id = message['image']['id']
            media_url = whatsapp_client.get_media_url(id=media_id)
            media_content = whatsapp_client.convert_to_base64(
                file=whatsapp_client.download_media(url=media_url)
            )
            
            return Message(
                **base_data,
                message_type='image',
                text=message['image'].get('caption', 'User sent image. Build your response based on the image and the context.'),
                media_id=media_id,
                media_content=media_content
            )
        
        elif 'audio' in message:
            media_id = message['audio']['id']
            media_url = whatsapp_client.get_media_url(id=media_id)
            # TODO: Perform extraction in separate file
            file = whatsapp_client.download_media(url=media_url)
            media_content = whatsapp_client.convert_to_base64(file=file)
            text = whatsapp_client.transcribe_audio(file=file)
            
            return Message(
                **base_data,
                message_type='audio',
                text=text,
                media_id=media_id,
                media_content=media_content,
            )
        
        elif 'document' in message:
            media_id = message['document']['id']
            media_url = whatsapp_client.get_media_url(id=media_id)
            file_type = message['document']['mime_type']
            media_content = parser.parse(
                file_bytes=whatsapp_client.download_media(url=media_url),
                file_type=file_type,
            )
            
            return Message(
                **base_data,
                message_type='document',
                text=message['document'].get('caption', 'User sent document. Build your response based on the content and the context.'),
                media_id=media_id,
                media_content=media_content,
            )
        else:
            raise ValueError('Lo siento, no puedo procesar este tipo de mensaje aún. He tomado nota y trabajaré para agregar soporte en el futuro.')
        
    except Exception as error_message:
        return Message(
            **base_data,
            message_type='unsupported',
            text=str(error_message),
        )


def build_response_message(user_message: Message, raw_response: str) -> Message:
    return Message(
        id=f'{user_message.id}-r',
        phone_number_id=user_message.phone_number_id,
        sender='agent', 
        phone_number=user_message.phone_number,
        message_type='text',
        text=raw_response,
        timestamp=time(),
    )