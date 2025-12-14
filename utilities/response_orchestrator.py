# Init
from init.whatsapp import whatsapp_client

# Utilities
from utilities.authentication import sign
from utilities.message_parser import build_agent_message

# Agents
from agents.base_agent import initialize_base_agent

# Data
from data.models import Message

# Standard
import random

def orchestrate_response(user_message: Message):
    if user_message.message_type in ['text', 'audio', 'image', 'video', 'document']:
        raw_response = initialize_base_agent(user_message=user_message)
        response_message = build_agent_message(user_message=user_message, raw_response=raw_response)
        response = whatsapp_client.send_message(response_message=response_message)

    elif user_message.message_type == 'sticker':
        with open(f'stickers/{random.randint(1, 11)}.webp', 'rb') as file:
            file_content = file.read()

        media_id = whatsapp_client.upload_media(message=user_message, file_content=file_content, file_name='sticker.webp', file_type='image/webp')
        raw_response = 'Que bonito sticker! Gracias por compartir 🌈'
        response_message = build_agent_message(user_message=user_message, raw_response=raw_response, message_type='sticker', media_id=media_id)
        response = whatsapp_client.send_media(message=response_message, media_id=response_message.media_id, file_name='sticker.webp', file_type='sticker')

    # Unsupported/Unsuscribed Features
    elif 'unsupported' in user_message.message_type:
        raw_response = 'Lo siento, no puedo procesar este tipo de mensaje aún. He tomado nota y trabajaré para agregar soporte en el futuro.'
        response_message = build_agent_message(user_message=user_message, raw_response=raw_response)
        response = whatsapp_client.send_message(response_message=response_message)
    else:
        raw_response = 'Rayos! No cuentas con acceso a esta funcionalidad. Adquiere una suscripción con más beneficios para disfrutar de esta y muchas otras funciones. 🚀\n\n👉 https://app.recurrente.com/s/colegios-com/plan-pro'
        response_message = build_agent_message(user_message=user_message, raw_response=raw_response)
        response = whatsapp_client.send_message(response_message=response_message)
    
    if 'messages' not in response:
        return None
    return response_message
