# Init
from init.fast_api import app
from init.whatsapp import whatsapp_client
import init.firebase

# Typing
from typing import Optional

# Utilities
from utilities.account import create_subscription, verify_user, verify_subscription
from utilities.authentication import verify
from utilities.cryptography import decrypt_request, encrypt_response
from utilities.message_parser import verify_message_payload, is_duplicate_message, build_user_message
from utilities.response_orchestrator import orchestrate_response
from utilities.reminder_manager import process_reminders

# Storage
from storage.storage import save_data, get_data

# Agents
from agents.memory import initialize_memory_workflow

# Async
from fastapi import Request, Response, Query, BackgroundTasks, HTTPException

# Standard
import time


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

    if not verify_message_payload(payload):
        return 'Invalid request.'
    
    if is_duplicate_message(payload):
        return 'Message already exists.'
    
    user_message = build_user_message(payload)

    if not verify_user(user_message=user_message):
        return 'User created successfully.'
    
    subscription_type = verify_subscription(user_message=user_message)

    if not subscription_type:
        return 'Subscription expired.'
    
    whatsapp_client.send_reaction(user_message=user_message, reaction='💭')

    response_message, response = orchestrate_response(user_message=user_message, subscription_type=subscription_type)
    if not response_message:
        return 'Error sending response.'

    whatsapp_client.send_reaction(user_message=user_message)
    
    response_message.id = response['messages'][0]['id'].replace('wamid.', '')
    background_tasks.add_task(initialize_memory_workflow, user_message, response_message)

    end = time.time()
    print(f'Time elapsed: {end - start}')

    return True

               
@app.post('/renew_subscription/')
def renew_subscription(request: Request, payload: dict):
    headers = request.headers
    if headers['origin'] == 'Nf8Sa!EGM3%&cKyIcyy%In$@vZ^klOI!':
        phone_number = create_subscription(payload)
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
        if content_type == 'intake' or content_type == 'profile':
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
        if content_type == 'intake' or content_type == 'profile':
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
    

@app.get('/send_reminders/')
def send_reminders():
    try:    
        start = time.time()
        process_reminders()
        end = time.time()
        print(f'Time elapsed: {end - start}')
        return f'Reminders processed successfully.'
    except:
        return 'Error sending reminders.'


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