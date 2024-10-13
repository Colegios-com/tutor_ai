# Init
from init.fast_api import app
from init.whatsapp import whatsapp_client
import init.firebase

# Utilities
from utilities.parsing import repair_json_response
from utilities.embedding import embed_data
from utilities.vector_storage import save_vectors, get_vectors, delete_vectors, query_vectors
from utilities.storage import save_data, get_data, update_data, delete_data
from utilities.transformer import generate_descriptors, stream_rewrite, stream_generate, batch_optimize, batch_respond
from utilities.classifier import classify
from utilities.templates import get_template_data
from utilities.whatsapp import save_message, get_messages


# Models
from data.models import Parameters, Template
from fastapi import WebSocket, Request, HTTPException, Query

from starlette.concurrency import run_in_threadpool

from datetime import datetime
import jwt
import json
import os


def verify(authorization_token):
    jwt_key = os.environ.get('JWT_KEY')

    try:
        user = jwt.decode(authorization_token, jwt_key, algorithms=["HS256"])
    except KeyError:
        raise HTTPException(status_code=401, detail='Authorization header is missing.')
    except jwt.DecodeError:
        raise HTTPException(status_code=401, detail='Invalid token.')
    except jwt.InvalidSignatureError:
        raise HTTPException(status_code=401, detail='Invalid signature.')
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Token has expired.')

    return True


@app.post('/embeddings/')
def post_embeddings(template: Template) -> str:
    raw_descriptors = generate_descriptors(template=template)
    descriptors = raw_descriptors.strip().split('|')
    embeddings = embed_data(data=descriptors)
    save_vectors(identifier=template.id, data=descriptors, embeddings=embeddings)
    return 'Data embedded successfully.'


@app.delete('/embeddings/{id}/')
def delete_embeddings(id: str) -> str:
    success = delete_vectors(id=id)
    return 'Data deleted successfully.' if success else 'Data deletion failed.'


@app.post('/bot/colegios/rewrite/')
def colegios_rewrite_view(parameters: Parameters, request: Request) -> dict:
    if(verify(request)):
        old_template = get_template_data(request, parameters.template)
        intent = determine_intent(f'{old_template["title"]}: {parameters.instructions}')
        if intent == 'new_document':
            template_id = query_templates(parameters.instructions)
            template = get_template_data(request, template_id)
            if template is not None:
                if parameters.seed:
                    instructions = colegios_optimization_bot(parameters.seed, parameters.instructions)
                    parameters.instructions = instructions
                raw_response = colegios_document_bot(parameters, template)
                response = stitch_response(raw_response)
                return {'template': template_id, 'content': response}
        else:
            raw_response = colegios_rewrite_bot(parameters)
            response = stitch_response(raw_response)
            return {'template': parameters.template, 'content': response}
     

@app.websocket('/generate/')
async def generate_document(websocket: WebSocket) -> str:
    await websocket.accept()
    try:
        while True:
            # Wait for the client to send a message
            json_data = await websocket.receive_json()

            # Set authorization and parameters
            if json_data:
                authorization_token = json_data['headers']['Authorization']
                if not verify(authorization_token):
                    await websocket.send_text('Invalid authorization token.')
                    return

            parameters = Parameters(**json_data['parameters'])

            intent = 'new_document'
            # Check intent for seeded documents
            if parameters.seed:
                # If seeded, determine intent
                old_template = await run_in_threadpool(get_template_data, authorization_token, parameters.template)
                intent = await run_in_threadpool(classify, f'{old_template["title"]}: {parameters.instructions}')

                # If rewrite, rewrite document
                if intent == 'rewrite':
                    raw_response = await stream_rewrite(websocket, parameters)
                    if raw_response:
                        await websocket.send_text(raw_response)
                    else:
                        await websocket.send_text('END_OF_RESPONSE')
                # If new document, determine intended template and generate
                else:
                    template_id = await query_data(parameters.instructions)
                    template = await run_in_threadpool(get_template_data, authorization_token, template_id)
                    raw_response = await stream_generate(websocket, parameters, template)
                    if raw_response:
                        await websocket.send_text(raw_response)
                    else:
                        await websocket.send_text(f'TEMPLATE_ID:{template_id}')
                        await websocket.send_text('END_OF_RESPONSE')

            else:
                # If not seeded, create new document
                template = await run_in_threadpool(get_template_data, authorization_token, parameters.template)
                raw_response = await stream_generate(websocket, parameters, template)
                if raw_response:
                    await websocket.send_text(raw_response)
                else:
                    await websocket.send_text('END_OF_RESPONSE')
                    
    finally:
        await websocket.close()


@app.get('/whatsapp/')
async def whatsapp_webhook(hub_mode: str = Query(..., alias='hub.mode'), hub_challenge: int = Query(..., alias='hub.challenge'), hub_verify_token: str = Query(..., alias='hub.verify_token')):
    if hub_mode == 'subscribe' and hub_verify_token == '!MdA3tCPvdyIdPg&':
        return hub_challenge
    else:
        return 'Invalid request.'


@app.post('/whatsapp/')
async def whatsapp_webhook(request: Request):
    webhook_data = await request.json()
    if 'entry' in webhook_data and webhook_data['entry']:
        for entry in webhook_data['entry']:
            if 'changes' in entry:
                for change in entry['changes']:
                    if 'value' in change and 'messages' in change['value']:
                        messages = change['value']['messages']
                        for message in messages:
                            if 'from' in message and 'type' in message:
                                message_id = message['id']
                                phone_number = message['from']

                                whatsapp_client.send_reaction(to=phone_number, message_id=message_id, reaction='💬')
                                message_text = None
                                image_base64 = None

                                context = get_messages(phone_number=message['from'], message=message_text)


                                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                message['timestamp'] = now

                                if message['type'] == 'image':
                                    message_text = message['image']['caption'] if 'caption' in message['image'] else 'The student has not provided a message. Focus on the content on the image to resolve the question.'
                                    image_id = message['image']['id']
                                    save_message(message_id=message_id, phone_number=message['from'], message_dict=message, image_id=image_id)
                                    image_url = whatsapp_client.get_media(image_id)
                                    image_base64 = whatsapp_client.download_and_convert_to_base64(image_url)
                                elif message['type'] == 'text':
                                    message_text = message['text']['body']
                                    save_message(message_id=message_id, phone_number=message['from'], message_dict=message)

                                try:
                                    response = batch_respond(message_text, context, image_base64)
                                    result = whatsapp_client.send_message(to=phone_number, message=response)

                                    response_message = result['messages'][0]

                                    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                    response_message['from'] = 'agent'
                                    response_message['type'] = 'text'
                                    response_message['text'] = {'body': response}
                                    response_message['timestamp'] = now
                                    
                                    save_message(message_id=f'{message_id} agent', phone_number=message['from'], message_dict=response_message)

                                    whatsapp_client.send_reaction(to=phone_number, message_id=message_id, reaction='👍')

                                except Exception as e:
                                    print(f'Exception occurred while sending message: {str(e)}')
