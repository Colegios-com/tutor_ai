# Init
from init.fast_api import app
from init.whatsapp import whatsapp_client
import init.firebase

# Typing
from typing import Optional

# Utilities
from utilities.account import save_user, verify_subscription, verify_access
from utilities.analysis_workflow import initialize_analysis_workflow
from utilities.evaluation_workflow import initialize_evaluation_workflow
from utilities.guide_workflow import initialize_guide_workflow
from utilities.memory_workflow import initialize_memory_workflow
from utilities.storage import save_data, get_data
from utilities.tutor_workflow import initialize_tutor_workflow
from utilities.whatsapp import verify_message, build_user_message, build_response_message, check_message

# Async
from fastapi import Request, Query, BackgroundTasks, HTTPException

import random
import requests
import jwt
import json
import os


def sign(phone_number):
    jwt_key = os.environ.get('JWT_KEY')

    if not jwt_key:
        raise HTTPException(status_code=401, detail='JWT key is missing.')

    try:
        web_token = jwt.encode({'phone_number': phone_number}, jwt_key, algorithm='HS256')
        return web_token
    except jwt.InvalidKeyError:
        raise HTTPException(status_code=401, detail='Invalid key.')
    except jwt.InvalidAlgorithmError:
        raise HTTPException(status_code=401, detail='Invalid algorithm.')
    except Exception:
        raise HTTPException(status_code=401, detail='Token creation failed.')


def verify(authorization_token):
    jwt_key = os.environ.get('JWT_KEY')

    if not jwt_key:
        raise HTTPException(status_code=401, detail='JWT key is missing.')
        
    try:
        user = jwt.decode(authorization_token, jwt_key, algorithms=["HS256"])
        return user['phone_number']
    except jwt.InvalidKeyError:
        raise HTTPException(status_code=401, detail='Invalid key.')
    except jwt.InvalidAlgorithmError:
        raise HTTPException(status_code=401, detail='Invalid algorithm.')
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Token has expired.')
    except jwt.DecodeError:
        raise HTTPException(status_code=401, detail='Invalid token.')
    except Exception:
        raise HTTPException(status_code=401, detail='Token verification failed.')

# @app.get('/webhooks/')
# def whatsapp_webhooks():
#     response = whatsapp_client.list_webhooks()
#     return response


# @app.post('/webhooks/')
# def whatsapp_webhooks():
#     response = whatsapp_client.add_webhook()
#     return response


# @app.delete('/webhooks/')
# def whatsapp_webhooks():
#     response = whatsapp_client.delete_webhook()
#     return response


@app.get('/whatsapp/')
async def whatsapp_webhook(hub_mode: str = Query(..., alias='hub.mode'), hub_challenge: int = Query(..., alias='hub.challenge'), hub_verify_token: str = Query(..., alias='hub.verify_token')):
    if hub_mode == 'subscribe' and hub_verify_token == '!MdA3tCPvdyIdPg&':
        return hub_challenge
    else:
        return 'Invalid request.'


@app.post('/whatsapp/', status_code=200)
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    payload = await request.json()

    if not verify_message(payload):
        return 'Invalid request.'
    
    # TODO: Build message after all verifications
    user_message = build_user_message(payload)

    print(user_message)

    subscription_type = verify_subscription(user_message.phone_number)
    if not subscription_type:
        return 'Subscription not found.'

    if check_message(user_message):
        return 'Message already exists.'
    
    debug = verify_access(user_message.phone_number)

    whatsapp_client.send_reaction(user_message=user_message, reaction='💭')

    # Starter Features
    if user_message.message_type in ['text', 'image', 'audio']:
        raw_response = initialize_tutor_workflow(user_message=user_message, debug=debug)
        response_message = build_response_message(user_message=user_message, raw_response=raw_response)
        response = whatsapp_client.send_message(response_message=response_message)
    # Starter Commands
    elif user_message.message_type == '/perfil':
        raw_response = f'Claro! Aquí tienes el link a tu perfil. ✨ \n\nhttps://aldous.colegios.com/profile/{sign(user_message.phone_number)}/'
        response_message = build_response_message(user_message=user_message, raw_response=raw_response)
        response = whatsapp_client.send_message(response_message=response_message)
    # Pro Features
    elif user_message.message_type == 'document' and subscription_type in ['pro', 'unlimited', 'tester']:
        raw_response = initialize_tutor_workflow(user_message=user_message, debug=debug)
        response_message = build_response_message(user_message=user_message, raw_response=raw_response)
        response = whatsapp_client.send_message(response_message=response_message)
    # Pro Commands
    elif user_message.message_type == '/guia' and subscription_type in ['pro', 'unlimited', 'tester']:
        guide_text = initialize_guide_workflow(user_message=user_message)
        media_id = whatsapp_client.upload_media(message=user_message, file_content=guide_text, file_name='guiaDeEstudio.md', file_type='text/plain')
        raw_response = 'Claro! Aquí tienes tu guía de estudio. 📚'
        response_message = build_response_message(user_message=user_message, raw_response=raw_response, message_type='document', media_id=media_id, media_content=guide_text)
        response = whatsapp_client.send_media(message=user_message, media_id=media_id, file_name='guiaDeEstudio.md', file_type='document', caption='Aquí está tu guía de estudio personalizada. 💡')
    elif user_message.message_type == '/examen' and subscription_type in ['pro', 'unlimited', 'tester']:
        evaluation_id = initialize_evaluation_workflow(user_message=user_message)
        raw_response = f'Claro! Aquí tienes tu examen personalizado 📝 \n\nhttps://aldous.colegios.com/evaluation/{evaluation_id}/{sign(user_message.phone_number)}/'
        response_message = build_response_message(user_message=user_message, raw_response=raw_response)
        response = whatsapp_client.send_message(response_message=response_message)
    # Unlimited Commands
    elif user_message.message_type == '/analisis' and subscription_type in ['unlimited', 'tester']:
        analysis_text = initialize_analysis_workflow(user_message=user_message)
        media_id = whatsapp_client.upload_media(message=user_message, file_content=analysis_text, file_name='analisisPersonalizado.md', file_type='text/markdown')
        raw_response = 'Claro! Aquí tienes tu análisis. 📊'
        response_message = build_response_message(user_message=user_message, raw_response=raw_response, message_type='document', media_id=media_id, media_content=analysis_text)
        response = whatsapp_client.send_media(message=user_message, media_id=media_id, file_name='analisisPersonalizado.md', file_type='document', caption='Aquí está tu análisis personalizado. 🧠')
    # Unsupported/Unsuscribed Features
    elif user_message.message_type == 'unsupported':
        raw_response = 'Lo siento, no puedo procesar este tipo de mensaje aún. He tomado nota y trabajaré para agregar soporte en el futuro. 🤖'
        response_message = build_response_message(user_message=user_message, raw_response=raw_response)
        response = whatsapp_client.send_message(response_message=response_message)
    else:
        raw_response = 'Rayos! No cuentas con acceso a esta funcionalidad. Adquiere una suscripción con más beneficios para disfrutar de esta y muchas otras funciones. 🚀\n\n👉 https://app.recurrente.com/s/colegios-com/plan-pro'
        response_message = build_response_message(user_message=user_message, raw_response=raw_response)
        response = whatsapp_client.send_message(response_message=response_message)
    

    # Overwrite response ID
    if 'messages' not in response:
        print(f'No messages in response: {response}')
        return False
    
    response_message.id = response['messages'][0]['id'].replace('wamid.', '')

    background_tasks.add_task(initialize_memory_workflow, user_message, response_message)
    random_reaction = random.choice(['🖍️', '✏️', '🖊️'])
    whatsapp_client.send_reaction(user_message=user_message, reaction=random_reaction)

    return True

               
@app.post('/renew_subscription/')
def renew_subscription(request: Request, payload: dict):
    headers = request.headers
    if headers['origin'] == 'Nf8Sa!EGM3%&cKyIcyy%In$@vZ^klOI!':
        phone_number = save_user(payload)
        whatsapp_client.send_template(phone_number=phone_number, template_name='subscription_activated')
        return 'Subscription renewed successfully.'
    else:
        return 'Unauthorized request.'


@app.get('/get_content/')
def get_content(request: Request, content_type: str, content_id: Optional[str] = None):
    headers = request.headers
    try:
        phone_number = verify(headers['Authorization'])
        if content_type == 'profile':
            url = f'users/{phone_number}/profile'
        elif content_type == 'evaluations':
            url = f'users/{phone_number}/evaluations/{content_id}'
        else:
            raise HTTPException(status_code=404, detail='Content type not found.')
        
        data = get_data(url)
        return data
    except:
        return 'Unauthorized request.'


@app.post('/update_content/')
def update_content(request: Request, payload: dict, content_type: str, content_id: Optional[str] = None):
    headers = request.headers
    try:
        phone_number = verify(headers['Authorization'])
        if content_type == 'profile':
            url = f'users/{phone_number}/profile'
        elif content_type == 'evaluations':
            url = f'users/{phone_number}/evaluations/{content_id}'
        else:
            raise HTTPException(status_code=404, detail='Content type not found.')
        save_data(url, payload)
        return 'Content updated successfully.'
    except:
        return 'Unauthorized request.'