# Init
from init.fast_api import app
from init.whatsapp import whatsapp_client
import init.firebase

# Utilities
from utilities.account import save_user, verify_subscription, verify_access
from utilities.analysis_workflow import initialize_analysis_workflow
from utilities.memory_workflow import initialize_memory_workflow
from utilities.tutor_workflow import initialize_tutor_workflow
from utilities.whatsapp import verify_message, build_user_message, build_response_message, check_message

# Async
from fastapi import Request, HTTPException, Query, BackgroundTasks

import random
import time
import jwt
import os


def verify(authorization_token):
    jwt_key = os.environ.get('JWT_KEY')

    try:
        user = jwt.decode(authorization_token, jwt_key, algorithms=['HS256'])
    except KeyError:
        raise HTTPException(status_code=401, detail='Authorization header is missing.')
    except jwt.DecodeError:
        raise HTTPException(status_code=401, detail='Invalid token.')
    except jwt.InvalidSignatureError:
        raise HTTPException(status_code=401, detail='Invalid signature.')
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Token has expired.')

    return True


@app.get('/whatsapp/')
async def whatsapp_webhook(hub_mode: str = Query(..., alias='hub.mode'), hub_challenge: int = Query(..., alias='hub.challenge'), hub_verify_token: str = Query(..., alias='hub.verify_token')):
    if hub_mode == 'subscribe' and hub_verify_token == '!MdA3tCPvdyIdPg&':
        return hub_challenge
    else:
        return 'Invalid request.'


@app.post('/whatsapp/', status_code=200)
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    start = time.time()
    payload = await request.json()

    if not verify_message(payload):
        print('Invalid request.')
        return 'Invalid request.'
    
    message = build_user_message(payload)

    if not verify_subscription(message.phone_number):
        print('Subscription not found.')
        return 'Subscription not found.'

    if check_message(message):
        print('Message already exists.')
        return 'Message already exists.'
    
    debug = verify_access(message.phone_number)

    # Workflow
    whatsapp_client.send_reaction(message=message, reaction='💭')

    if message.message_type == '/analisis':
        media_id = whatsapp_client.upload_media(message)
        raw_response = 'Claro! Aquí tienes tu análisis. 📊'
        response_message = build_response_message(message, raw_response)
        response = whatsapp_client.send_media(message=message, media_id=media_id)
    else:
        raw_response = initialize_tutor_workflow(message, debug=debug)
        response_message = build_response_message(message, raw_response)
        response = whatsapp_client.send_message(message=response_message)
    

    # Overwrite response ID
    response_message.id = response['messages'][0]['id'].replace('wamid.', '')

    background_tasks.add_task(initialize_memory_workflow, message, response_message)

    random_reaction = random.choice(['🖍️', '✏️', '🖊️'])
    whatsapp_client.send_reaction(message=message, reaction=random_reaction)

    end = time.time()
    print(f'Elapsed time: {end - start} seconds')
    return True

                        
@app.post('/renew_subscription/')
def renew_subscription(payload: dict):
    phone_number = save_user(payload)
    whatsapp_client.send_template(phone_number=phone_number, template_name='subscription_activated')
    return 'Subscription renewed successfully.'


@app.post('/generate_analysis/')
def generate_analysis(phone_number: str):
    synthesis = initialize_analysis_workflow(phone_number=phone_number)
    return synthesis
