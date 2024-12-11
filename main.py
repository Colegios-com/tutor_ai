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


@app.get('/webhooks/')
def whatsapp_webhooks():
    response = whatsapp_client.list_webhooks()
    return response


@app.post('/webhooks/')
def whatsapp_webhooks():
    response = whatsapp_client.add_webhook()
    return response


@app.delete('/webhooks/')
def whatsapp_webhooks():
    response = whatsapp_client.delete_webhook()
    return response


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
    
    message = build_user_message(payload)

    if not verify_subscription(message.phone_number):
        return 'Subscription not found.'

    if check_message(message):
        return 'Message already exists.'
    
    debug = verify_access(message.phone_number)

    whatsapp_client.send_reaction(message=message, reaction='💭')

    if message.message_type == '/analisis':
        analysis_text = initialize_analysis_workflow(message=message)
        media_id = whatsapp_client.upload_media(message=message, analysis_text=analysis_text)
        raw_response = 'Claro! Aquí tienes tu análisis. 📊'
        response_message = build_response_message(message=message, raw_response=raw_response)
        response = whatsapp_client.send_media(message=message, media_id=media_id)
    if message.message_type == '/examen':
        evaluation_id = initialize_evaluation_workflow(message=message, debug=debug)
        raw_response = f'Claro! Aquí tienes tu examen personalizado. 📝 \n\nhttps://aldous.colegios.com/evaluation/{message.phone_number}/{evaluation_id}'
        response_message = build_response_message(message=message, raw_response=raw_response)
        response = whatsapp_client.send_message(message=response_message)
    else:
        raw_response = initialize_tutor_workflow(message=message, debug=debug)
        response_message = build_response_message(message=message, raw_response=raw_response)
        response = whatsapp_client.send_message(message=response_message)
    

    # Overwrite response ID
    if 'messages' not in response:
        return False
    
    response_message.id = response['messages'][0]['id'].replace('wamid.', '')

    background_tasks.add_task(initialize_memory_workflow, message, response_message)
    random_reaction = random.choice(['🖍️', '✏️', '🖊️'])
    whatsapp_client.send_reaction(message=message, reaction=random_reaction)

    return True

               
@app.post('/renew_subscription/')
def renew_subscription(payload: dict):
    phone_number = save_user(payload)
    whatsapp_client.send_template(phone_number=phone_number, template_name='subscription_activated')
    return 'Subscription renewed successfully.'


@app.post('/generate_evaluation/')
def generate_evaluation(payload: dict):
    evaluation = initialize_evaluation_workflow(payload)
    return evaluation
