
from io import BytesIO

import requests
import json
import random


class WhatsappClient:
    def __init__(self, key):
        self.key = key

    
    def get_settings(self):
        # CALL: Need to generate System User token with higher permissions to get the settings
        url = f'https://graph.facebook.com/v22.0/389338054272783/settings' # Phone Number ID
        
        headers = {
            'Authorization': f'Bearer {self.key}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(url, headers=headers)
        return response.json()

    def add_public_key(self):

        url = f'https://graph.facebook.com/v22.0/389338054272783/whatsapp_business_encryption' # Phone Number ID
        
        headers = {
            'Authorization': f'Bearer {self.key}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        data = {
            'business_public_key': 'PUBLIC_KEY'
        }

        try:
            response = requests.post(url, data=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return f'Error making request: {e}'


    def list_webhooks(self):        
        url = f'https://graph.facebook.com/v22.0/447464381784934/subscribed_apps' # Business Account ID
        
        headers = {
            'Authorization': f'Bearer {self.key}',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return f'Error making request: {e}'
        
    
    def delete_webhook(self):

        url = f'https://graph.facebook.com/v22.0/447464381784934/subscribed_apps' # Business Account ID
        
        headers = {
            'Authorization': f'Bearer {self.key}',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.delete(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return f'Error making request: {e}'
        

    def add_webhook(self):

        url = f'https://graph.facebook.com/v22.0/447464381784934/subscribed_apps' # Business Account ID
        
        headers = {
            'Authorization': f'Bearer {self.key}',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return f'Error making request: {e}'

    
    def send_typing_indicator(self, user_message):
        try:
            headers = {
                'Authorization': f'Bearer {self.key}',
                'Content-Type': 'application/json'
            }
            payload = {
                "messaging_product": "whatsapp",
                "status": "read",
                "message_id": user_message.whatsapp_message_id,
                "typing_indicator": {
                    "type": "text"
                }
                
            }
            response = requests.post(
                f'https://graph.facebook.com/v22.0/{user_message.phone_number_id}/messages', 
                headers=headers, 
                data=json.dumps(payload)
            )
            if response.status_code == 200:
                return True
            else:
                raise Exception
        except Exception as e:
            return {'status': False, 'message': f'Oops, there was an error sending the typing indicator: {e}'}
    

    def send_reaction(self, user_message, reaction=None):
        try:
            if not reaction:
                reaction = random.choice(['🖍️', '✏️', '🖊️'])
            headers = {
                'Authorization': f'Bearer {self.key}',
                'Content-Type': 'application/json'
            }

            payload = {
                'messaging_product': 'whatsapp',
                'recipient_type': 'individual',
                'to': user_message.wa_id,
                'type': 'reaction',
                'reaction': {
                    'message_id': user_message.whatsapp_message_id,
                    'emoji': reaction
                }
            }

            response = requests.post(
                f'https://graph.facebook.com/v22.0/{user_message.phone_number_id}/messages', 
                headers=headers, 
                data=json.dumps(payload)
            )
            if response.status_code == 200:
                return True
            else:
                raise Exception
        except Exception as e:
            return {'status': False, 'message': f'Oops, there was an error sending the message: {e}'}

    
    def send_template(self, wa_id, template_name, components=None):
        try:
            headers = {
                'Authorization': f'Bearer {self.key}',
                'Content-Type': 'application/json'
            }

            payload = {
                'messaging_product': 'whatsapp',
                'recipient_type': 'individual',
                'to': wa_id,
                'type': 'template',
                'template': {
                    'name': template_name,
                    'language': {
                        'code': 'en'
                    },
                }
            }
            if components:
                payload['template']['components'] = components
            response = requests.post(
                f'https://graph.facebook.com/v22.0/389338054272783/messages', # Phone Number ID
                headers=headers, 
                data=json.dumps(payload)
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception
        except Exception as e:
            return {'status': False, 'message': f'Oops, there was an error sending the message: {e}'}


    def send_message(self, response_message):
        try:
            headers = {
                'Authorization': f'Bearer {self.key}',
                'Content-Type': 'application/json'
            }

            payload = {
                'messaging_product': 'whatsapp',
                'to': response_message.wa_id,
                'type': 'text',
                'text': {
                    'body': response_message.text,
                }
            }
            response = requests.post(
                f'https://graph.facebook.com/v22.0/{response_message.phone_number_id}/messages', 
                headers=headers, 
                data=json.dumps(payload)
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception
        except Exception as e:
            return {'status': False, 'message': f'Error sending message: {e}'}


    def get_media_url(self, id):
        try:
            url = f'https://graph.facebook.com/v22.0/{id}'
            
            headers = {
                'Authorization': f'Bearer {self.key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                media_data = response.json()
                return media_data['url'], media_data['mime_type']
            else:
                raise Exception
        except Exception as e:
            return {'status': False, 'message': f'Oops, there was an error retrieving the image URL: {e}'}


    def download_media(self, url):
        headers = {
            'Authorization': f'Bearer {self.key}',
            'Content-Type': 'application/json'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.content
        else:
            return None
        

    def upload_media(self, message, file_content, file_name, file_type):
        try:
            if file_type == 'text/plain':
                content_bytes = BytesIO(file_content.encode('utf-8'))
            else:
                content_bytes = BytesIO(file_content)
            
            headers = {
                'Authorization': f'Bearer {self.key}'
            }

            files = {
                'file': (file_name, content_bytes, file_type)
            }

            response = requests.post(
                f'https://graph.facebook.com/v22.0/{message.phone_number_id}/media',
                data={
                    'messaging_product': 'whatsapp',
                    'type': file_type
                },
                files=files,
                headers=headers
            )

            if response.status_code == 200:
                media_data = response.json()
                return media_data['id']
            else:
                raise Exception(f'Upload failed: {response.text}')

        except Exception as e:
            return {'status': False, 'message': f'Error uploading analysis: {e}'}
        

    def send_media(self, message, media_id, file_name, file_type, caption=None):
        try:
            headers = {
                'Authorization': f'Bearer {self.key}',
                'Content-Type': 'application/json'
            }

            payload = {
                'messaging_product': 'whatsapp',
                'recipient_type': 'individual',
                'to': message.wa_id,
                'type': file_type,
            }

            if file_type == 'image':
                payload['image'] = {
                    'id': media_id,
                    'caption': caption,
                }
            elif file_type == 'sticker':
                payload['sticker'] = {
                    'id': media_id,
                }
            elif file_type == 'audio':
                payload['audio'] = {
                    'id': media_id,
                    'caption': 'Audio Generado',
                }
            elif file_type == 'document':
                payload['document'] = {
                    'id': media_id,
                    'caption': caption,
                    'filename': file_name,
                }
            response = requests.post(
                f'https://graph.facebook.com/v22.0/{message.phone_number_id}/messages',
                headers=headers,
                data=json.dumps(payload)
            )

            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f'Send failed: {response.text}')

        except Exception as e:
            return {'status': False, 'message': f'Error sending document: {e}'}