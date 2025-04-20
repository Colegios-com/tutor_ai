# Init
from init.whatsapp import whatsapp_client

# Utilities
from utilities.authentication import sign
from utilities.message_parser import build_agent_message

# Agents
from agents.analysis import initialize_analysis_workflow
from agents.evaluation import initialize_evaluation_workflow
from agents.guide import initialize_guide_workflow
from agents.tutor import initialize_tutor_workflow
from agents.reminder import initialize_reminder_workflow
from agents.onboarding import initialize_onboarding_workflow
# Data
from data.models import Message

# Standard
import random

def orchestrate_response(user_message: Message, subscription_type: str):
    if user_message.message_type in ['text', 'audio']:
        raw_response = initialize_tutor_workflow(user_message=user_message)
        response_message = build_agent_message(user_message=user_message, raw_response=raw_response)
        response = whatsapp_client.send_message(response_message=response_message)
    elif user_message.message_type == 'sticker':
        with open(f'stickers/{random.randint(1, 11)}.webp', 'rb') as file:
            file_content = file.read()
        media_id = whatsapp_client.upload_media(message=user_message, file_content=file_content, file_name='sticker.webp', file_type='image/webp')
        raw_response = 'Que bonito sticker! Gracias por compartir 🌈'
        response_message = build_agent_message(user_message=user_message, raw_response=raw_response, message_type='sticker', media_id=media_id)
        response = whatsapp_client.send_media(message=response_message, media_id=response_message.media_id, file_name='sticker.webp', file_type='sticker')
    # Starter Commands
    elif user_message.message_type == '/perfil':
        raw_response = f'Claro! Aquí tienes el link a tu perfil. ✨ \n\nhttps://aldous.colegios.com/profile/{sign(user_message.phone_number)}/'
        response_message = build_agent_message(user_message=user_message, raw_response=raw_response)
        response = whatsapp_client.send_message(response_message=response_message)
    
    
    # Pro Features
    elif user_message.message_type in ['image', 'document'] and subscription_type in ['pro', 'unlimited', 'tester']:
        raw_response = initialize_tutor_workflow(user_message=user_message)
        response_message = build_agent_message(user_message=user_message, raw_response=raw_response)
        response = whatsapp_client.send_message(response_message=response_message)
    # Pro Commands
    elif user_message.message_type == '/guia' and subscription_type in ['pro', 'unlimited', 'tester']:
        guide_id = initialize_guide_workflow(user_message=user_message)
        raw_response = f'Claro! Aquí tienes tu guia personalizado 📝 \n\nhttps://aldous.colegios.com/guide/{guide_id}/{sign(user_message.phone_number)}/'
        
        response_message = build_agent_message(user_message=user_message, raw_response=raw_response)
        response = whatsapp_client.send_message(response_message=response_message)
    elif user_message.message_type == '/examen' and subscription_type in ['pro', 'unlimited', 'tester']:
        evaluation_id = initialize_evaluation_workflow(user_message=user_message)
        raw_response = f'Claro! Aquí tienes tu examen personalizado 📝 \n\nhttps://aldous.colegios.com/evaluation/{evaluation_id}/{sign(user_message.phone_number)}/'
        
        response_message = build_agent_message(user_message=user_message, raw_response=raw_response)
        response = whatsapp_client.send_message(response_message=response_message)
    
    # Unlimited Features
    elif user_message.message_type == 'video' and subscription_type in ['unlimited', 'tester']:
        raw_response = initialize_tutor_workflow(user_message=user_message)
        response_message = build_agent_message(user_message=user_message, raw_response=raw_response)
        response = whatsapp_client.send_message(response_message=response_message)
    # Unlimited Commands
    elif user_message.message_type == '/analisis' and subscription_type in ['unlimited', 'tester']:
        analysis_text = initialize_analysis_workflow(user_message=user_message)
        media_id = whatsapp_client.upload_media(message=user_message, file_content=analysis_text, file_name='analisisPersonalizado.md', file_type='text/plain')
        
        raw_response = 'Claro! Aquí tienes tu análisis personalizado. 📊'
        response_message = build_agent_message(user_message=user_message, raw_response=raw_response, message_type='document', media_id=media_id)
        response = whatsapp_client.send_media(message=user_message, media_id=media_id, file_name='analisisPersonalizado.md', file_type='document', caption='Aquí está tu análisis personalizado. 🧠')
    
    
    # Unsupported/Unsuscribed Features
    elif 'unsupported' in user_message.message_type:
        raw_response = 'Lo siento, no puedo procesar este tipo de mensaje aún. He tomado nota y trabajaré para agregar soporte en el futuro. 🤖'
        response_message = build_agent_message(user_message=user_message, raw_response=raw_response)
        response = whatsapp_client.send_message(response_message=response_message)
    else:
        raw_response = 'Rayos! No cuentas con acceso a esta funcionalidad. Adquiere una suscripción con más beneficios para disfrutar de esta y muchas otras funciones. 🚀\n\n👉 https://app.recurrente.com/s/colegios-com/plan-pro'
        response_message = build_agent_message(user_message=user_message, raw_response=raw_response)
        response = whatsapp_client.send_message(response_message=response_message)
    
    # Consider making while loop
    if 'messages' not in response:
        return False, False
    return response_message, response


def orchestrate_reminder(user_message: Message) -> tuple[Message, dict]:
    """
    Orchestrate the reminder response for a user
    Returns a tuple of (response_message, whatsapp_response)
    """
    try:
        reminder_text = initialize_reminder_workflow(user_message=user_message)
        if not reminder_text:
            return None, None

        response_message = build_agent_message(user_message=user_message, raw_response=reminder_text)
        response = whatsapp_client.send_message(response_message=response_message)

        return response_message, response
    except Exception as e:
        print(f'Error orchestrating reminder: {e}')
        return None, None
    

def orchestrate_onboarding_message(user_message: Message, default_onboarding_message: str) -> tuple[Message, dict]:
    """
    Orchestrate the onboarding message response for a user
    Returns a tuple of (response_message, whatsapp_response)
    """
    try:
        onboarding_text = initialize_onboarding_workflow(user_message=user_message, default_onboarding_message=default_onboarding_message)
        if not onboarding_text:
            return None, None

        response_message = build_agent_message(user_message=user_message, raw_response=onboarding_text)
        response = whatsapp_client.send_message(response_message=response_message)

        return response_message, response
    except Exception as e:
        print(f'Error orchestrating onboarding message: {e}')
        return None, None