# Init
from init.fast_api import app
from init.whatsapp import whatsapp_client
import init.firebase

# Utilities
from utilities.account import save_user, verify_subscription, verify_access
from utilities.analysis_workflow import initialize_analysis_workflow
from utilities.memory_workflow import initialize_memory_workflow
from utilities.evaluation_workflow import initialize_evaluation_workflow
from utilities.tutor_workflow import initialize_tutor_workflow
from utilities.whatsapp import verify_message, build_user_message, build_response_message, check_message

# Async
from fastapi import Request, Query, BackgroundTasks

import random
import json


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

    if not verify_subscription(user_message.phone_number):
        return 'Subscription not found.'

    if check_message(user_message):
        return 'Message already exists.'
    
    debug = verify_access(user_message.phone_number)

    whatsapp_client.send_reaction(user_message=user_message, reaction='💭')

    if user_message.message_type == '/perfil':
        raw_response = f'Claro! Aquí tienes el link a tu perfil ✨ \n\nhttps://aldous.colegios.com/profile/{user_message.phone_number}'
        response_message = build_response_message(user_message=user_message, raw_response=raw_response)
        response = whatsapp_client.send_message(response_message=response_message)
    elif user_message.message_type == '/analisis':
        analysis_text = initialize_analysis_workflow(user_message=user_message)
        media_id = whatsapp_client.upload_media(message=user_message, analysis_text=analysis_text)
        raw_response = 'Claro! Aquí tienes tu análisis. 📊'
        response_message = build_response_message(user_message=user_message, raw_response=raw_response)
        response = whatsapp_client.send_media(message=user_message, media_id=media_id)
    elif user_message.message_type == '/examen':
        evaluation_id = initialize_evaluation_workflow(user_message=user_message)
        raw_response = f'Claro! Aquí tienes tu examen personalizado 📝 \n\nhttps://aldous.colegios.com/evaluation/{user_message.phone_number}/{evaluation_id}'
        response_message = build_response_message(user_message=user_message, raw_response=raw_response)
        response = whatsapp_client.send_message(response_message=response_message)
    elif user_message.message_type == 'unsupported':
        raw_response = user_message.text
        response_message = build_response_message(user_message=user_message, raw_response=raw_response)
        response = whatsapp_client.send_message(response_message=response_message)
    else:
        raw_response = initialize_tutor_workflow(user_message=user_message, debug=debug)
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
def renew_subscription(payload: dict):
    phone_number = save_user(payload)
    whatsapp_client.send_template(phone_number=phone_number, template_name='subscription_activated')
    return 'Subscription renewed successfully.'
