# Init
from init.fast_api import app
from init.whatsapp import whatsapp_client
import init.firebase

# Typing
from typing import Optional

# Utilities
from utilities.account import save_user, verify_subscription, update_usage
from utilities.analysis_workflow import initialize_analysis_workflow
from utilities.cryptography import decrypt_request, encrypt_response
from utilities.evaluation_workflow import initialize_evaluation_workflow
from utilities.guide_workflow import initialize_guide_workflow
from utilities.memory_workflow import initialize_memory_workflow
from utilities.storage import save_data, get_data
from utilities.tutor_workflow import initialize_tutor_workflow
from utilities.whatsapp import verify_message, build_user_message, build_response_message, check_message

from utilities.guide import create_guide

# Async
from fastapi import Request, Response, Query, BackgroundTasks, HTTPException

import random
import jwt
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


# @app.post('/public_key/')
# def whatsapp_public_key():
#     response = whatsapp_client.add_public_key()
#     return response


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

    subscription_type = verify_subscription(user_message.phone_number)
    if subscription_type == 'new_user':
        with open(f'images/welcomeBanner.png', 'rb') as file:
            file_content = file.read()
        media_id = whatsapp_client.upload_media(message=user_message, file_content=file_content, file_name='image.png', file_type='image/png')
        raw_response = '¡Bienvenido! 🎉 *Soy Aldous, tu tutor virtual*. Tu prueba de 7 días está activada. ✅\n\nVeo que ya estás listo para aprender. *¿Cómo puedo ayudarte?*\n\nAquí te muestro algunas cosas que puedo hacer con tu plan actual (Starter):\n\n✨ **Procesamiento de Imágenes:** Envíame una foto de un problema matemático 📸 y te ayudaré a resolverlo. Por ejemplo: "Calcula el área de este triángulo".\n\n🎤 **Notas de Voz:** Explícame un tema en un audio 🗣️ y te daré un resumen o responderé tus preguntas. Por ejemplo: "Resume esta teoria sobre la relatividad".\n\n💬 **Conversación Natural:** ¡Habla conmigo como si estuvieras chateando con un amigo! Soy bueno para responder preguntas y explicar conceptos. Por ejemplo: "Explícame la diferencia entre mitosis y meiosis".\n\n¿Quieres aún más poder? 💪 Con los planes Pro y Unlimited, también puedes:\n\n📚 **Procesamiento de Documentos:** Comparte un documento 📝 (PDF, TXT) y te ayudaré a encontrar información clave o responder preguntas. Ejemplo: "Extrae los puntos principales de este PDF".\n\n📝 **Generación de Quizzes:** Pídeme que cree un cuestionario sobre cualquier tema. Ejemplo: "Crea un quiz sobre la Revolución Francesa".\n\n🗺️ **Generación de Guías:** Obtén una guía completa y detallada sobre un tema. Ejemplo: "Genera una guía sobre programación en Python".\n\n📊 **Generación de Análisis:** Analiza datos, textos o cualquier información que me proporciones. Ejemplo: "Analiza este texto y determina el sentimiento".\n\n¡Explora todo lo que puedo hacer y decide qué plan es perfecto para ti! 😉 ¡Estoy listo para empezar cuando tú lo estés! 🚀'
        response_message = build_response_message(user_message=user_message, raw_response=raw_response, message_type='image', media_id=media_id)
        response = whatsapp_client.send_media(message=response_message, media_id=response_message.media_id, file_name='image.png', file_type='image', caption=raw_response)
        whatsapp_client.send_reaction(user_message=user_message, reaction='😂')
        return 'New user.'
    elif not subscription_type:
        raw_response = 'Rayos! Tu suscripción ha caducado. Reactívala para disfrutar nuestro servicio. 🚀\n\n👉 https://app.recurrente.com/s/colegios-com/plan-pro'
        response_message = build_response_message(user_message=user_message, raw_response=raw_response)
        response = whatsapp_client.send_message(response_message=response_message)
        random_reaction = '💸'
        whatsapp_client.send_reaction(user_message=user_message, reaction=random_reaction)
        return 'Subscription not found.'
    

    if check_message(user_message):
        return 'Message already exists.'
    

    whatsapp_client.send_reaction(user_message=user_message, reaction='💭')

    # Starter Features
    if user_message.message_type in ['text', 'image', 'audio', 'video']:
        raw_response = initialize_tutor_workflow(user_message=user_message)
        response_message = build_response_message(user_message=user_message, raw_response=raw_response)
        response = whatsapp_client.send_message(response_message=response_message)
    elif user_message.message_type == 'sticker':
        sticker = random.randint(1, 11)
        with open(f'stickers/{sticker}.webp', 'rb') as file:
            file_content = file.read()
        media_id = whatsapp_client.upload_media(message=user_message, file_content=file_content, file_name='sticker.webp', file_type='image/webp')
        raw_response = 'Que bonito sticker 🌈'
        response_message = build_response_message(user_message=user_message, raw_response=raw_response, message_type='sticker', media_id=media_id)
        response = whatsapp_client.send_message(response_message=response_message)
        response = whatsapp_client.send_media(message=response_message, media_id=response_message.media_id, file_name='sticker.webp', file_type='sticker')
    # Starter Commands
    elif user_message.message_type == '/perfil':
        raw_response = f'Claro! Aquí tienes el link a tu perfil. ✨ \n\nhttps://aldous.colegios.com/profile/{sign(user_message.phone_number)}/'
        response_message = build_response_message(user_message=user_message, raw_response=raw_response)
        response = whatsapp_client.send_message(response_message=response_message)
    # Pro Features
    elif user_message.message_type == 'document' and subscription_type in ['pro', 'unlimited', 'tester']:
        raw_response = initialize_tutor_workflow(user_message=user_message)
        response_message = build_response_message(user_message=user_message, raw_response=raw_response)
        response = whatsapp_client.send_message(response_message=response_message)
    # Pro Commands
    elif user_message.message_type == '/guia' and subscription_type in ['pro', 'unlimited', 'tester']:
        guide_id = initialize_guide_workflow(user_message=user_message)
        raw_response = f'Claro! Aquí tienes tu guia personalizado 📝 \n\nhttps://aldous.colegios.com/guide/{guide_id}/{sign(user_message.phone_number)}/'
        response_message = build_response_message(user_message=user_message, raw_response=raw_response)
        response = whatsapp_client.send_message(response_message=response_message)
    elif user_message.message_type == '/examen' and subscription_type in ['pro', 'unlimited', 'tester']:
        evaluation_id = initialize_evaluation_workflow(user_message=user_message)
        raw_response = f'Claro! Aquí tienes tu examen personalizado 📝 \n\nhttps://aldous.colegios.com/evaluation/{evaluation_id}/{sign(user_message.phone_number)}/'
        response_message = build_response_message(user_message=user_message, raw_response=raw_response)
        response = whatsapp_client.send_message(response_message=response_message)
    # Unlimited Commands
    elif user_message.message_type == '/analisis' and subscription_type in ['unlimited', 'tester']:
        analysis_text = initialize_analysis_workflow(user_message=user_message)
        media_id = whatsapp_client.upload_media(message=user_message, file_content=analysis_text, file_name='analisisPersonalizado.md', file_type='text/plain')
        raw_response = 'Claro! Aquí tienes tu análisis personalizado. 📊'
        response_message = build_response_message(user_message=user_message, raw_response=raw_response, message_type='document', media_id=media_id, media_content=analysis_text)
        response = whatsapp_client.send_media(message=user_message, media_id=media_id, file_name='analisisPersonalizado.md', file_type='document', caption='Aquí está tu análisis personalizado. 🧠')
    # Unsupported/Unsuscribed Features
    elif 'unsupported' in user_message.message_type:
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

    random_reaction = random.choice(['🖍️', '✏️', '🖊️'])
    whatsapp_client.send_reaction(user_message=user_message, reaction=random_reaction)
    initialize_memory_workflow(user_message, response_message)
    update_usage(user_message)

    return True

               
@app.post('/renew_subscription/')
def renew_subscription(request: Request, payload: dict):
    headers = request.headers
    if headers['origin'] == 'Nf8Sa!EGM3%&cKyIcyy%In$@vZ^klOI!':
        phone_number = save_user(payload)
        components = [
            {
                'type': 'header',
                'parameters': [
                    {
                        'type': 'image',
                        'image': {
                        'link': 'https://colegios-media.s3.amazonaws.com/thumbnails/welcomeBanner.png'
                        },
                    },
                ],
            },
        ]
        whatsapp_client.send_template(phone_number=phone_number, template_name='subscription_activated', components=components)
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
        elif content_type == 'guides':
            url = f'users/{phone_number}/guides/{content_id}'
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
        elif content_type == 'guides':
            url = f'users/{phone_number}/guides/{content_id}'
        else:
            raise HTTPException(status_code=404, detail='Content type not found.')
        save_data(url, payload)
        return 'Content updated successfully.'
    except:
        return 'Unauthorized request.'
    

@app.post('/flow_test/')
async def flow_test(request: Request, background_tasks: BackgroundTasks):
    try:
        payload = await request.json()
        decrypted_data, aes_key, iv = decrypt_request(payload['encrypted_flow_data'], payload['encrypted_aes_key'], payload['initial_vector'])
        print(f'Decrypted data: {decrypted_data}')
        response = {"data": {"status": "active"}}

        encrypted_response = encrypt_response(response, aes_key, iv)
        return Response(content=encrypted_response, media_type='text/plain')
    except:
        return 'Unauthorized request.'
    

@app.get('/guide_test/')
def bot_test(request: Request):
    try:
        response = create_guide()
        return response
    except:
        return 'Unauthorized request.'
    


    


    # elif user_message.message_type == '/examen' and subscription_type in ['pro', 'unlimited', 'tester']:
    #     components = [
    #         {
    #             'type': 'body',
    #             'parameters': [
    #                 {
    #                     'type': 'text',
    #                     'parameter_name': 'first_name',
    #                     'text': 'Dudu',
    #                 },
    #             ],
    #         },
    #         {
    #             'type': 'button',
    #             'sub_type': 'flow',
    #             'index': '0',
    #             'parameters': [
    #                 {
    #                     'type': 'action',
    #                     'action': {
                 
    #                     }
    #                 }
    #             ]
    #         }
    #     ]
    #     whatsapp_client.send_template(phone_number=user_message.phone_number, template_name='test_flow', components=components)
    #     random_reaction = random.choice(['🖍️', '✏️', '🖊️'])
    #     whatsapp_client.send_reaction(user_message=user_message, reaction=random_reaction)
    #     return True