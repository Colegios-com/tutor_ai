from init.openai import openai_client

import requests
import base64
import json


class WhatsappClient:
    def __init__(self, key):
        self.key = key

    # Webhooks. ID is tied to phone number (API Setup in Developer Portal). Generate temporary Access Token.
    # Removed all extra apps from the Facebook Developer Portal. Only one app is needed.
    # Independent from Webhook in Configuration.


    def list_webhooks(self):        
        url = f'https://graph.facebook.com/v21.0/447464381784934/subscribed_apps'
        
        headers = {
            'Authorization': f'Bearer EAAPxOaWf7FUBOwI8ArF7ME4cvRBl13zSYz68PQSLanZBCP27NKZAbsRT3V0fuzmOh6Pq1sjajKLM83UvIs2e46VtKkEL4LKruzFoOSrkFD0JZC5B7utabMLsxUZBmHVdtc4F8Rr5ZCGFdZC8JZCPfSIdkqMgNrXoweYkCl3XrF7ZB5IldqohCp84jdI0KPxLNRqM2uI7DJkKtZAdUEbOnyYTvrjljHQZDZD',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return f'Error making request: {e}'
        
    
    def delete_webhook(self):

        url = f'https://graph.facebook.com/v21.0/447464381784934/subscribed_apps'
        
        headers = {
            'Authorization': f'Bearer EAAPxOaWf7FUBOwI8ArF7ME4cvRBl13zSYz68PQSLanZBCP27NKZAbsRT3V0fuzmOh6Pq1sjajKLM83UvIs2e46VtKkEL4LKruzFoOSrkFD0JZC5B7utabMLsxUZBmHVdtc4F8Rr5ZCGFdZC8JZCPfSIdkqMgNrXoweYkCl3XrF7ZB5IldqohCp84jdI0KPxLNRqM2uI7DJkKtZAdUEbOnyYTvrjljHQZDZD',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.delete(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return f'Error making request: {e}'
        

    def add_webhook(self):

        url = f'https://graph.facebook.com/v21.0/447464381784934/subscribed_apps'
        
        headers = {
            'Authorization': f'Bearer EAAPxOaWf7FUBOwI8ArF7ME4cvRBl13zSYz68PQSLanZBCP27NKZAbsRT3V0fuzmOh6Pq1sjajKLM83UvIs2e46VtKkEL4LKruzFoOSrkFD0JZC5B7utabMLsxUZBmHVdtc4F8Rr5ZCGFdZC8JZCPfSIdkqMgNrXoweYkCl3XrF7ZB5IldqohCp84jdI0KPxLNRqM2uI7DJkKtZAdUEbOnyYTvrjljHQZDZD',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return f'Error making request: {e}'
    

    def send_reaction(self, message, reaction):
        try:
            headers = {
                'Authorization': f'Bearer {self.key}',
                'Content-Type': 'application/json'
            }

            payload = {
                'messaging_product': 'whatsapp',
                'recipient_type': 'individual',
                'to': message.phone_number,
                'type': 'reaction',
                'reaction': {
                    'message_id': message.id,
                    'emoji': reaction
                }
            }

            response = requests.post(
                f'https://graph.facebook.com/v21.0/{message.phone_number_id}/messages', 
                headers=headers, 
                data=json.dumps(payload)
            )
            if response.status_code == 200:
                return True
            else:
                raise Exception
        except Exception as e:
            return {'status': False, 'message': f'Oops, there was an error sending the message: {e}'}

    
    def send_template(self, phone_number, template_name):
        try:
            headers = {
                'Authorization': f'Bearer {self.key}',
                'Content-Type': 'application/json'
            }

            payload = {
                'messaging_product': 'whatsapp',
                'recipient_type': 'individual',
                'to': phone_number,
                'type': 'template',
                'template': {
                    'name': template_name,
                    'language': {
                        'code': 'en'
                    },
                    'components': [
                        {
                            'type': 'header',
                            'parameters': [
                                {
                                    'type': 'image',
                                    'image': {
                                    'link': 'https://colegios-media.s3.amazonaws.com/thumbnails/welcomeBanner.png'
                                    }
                                }
                            ]
                        },
                    ]
                }
            }
            response = requests.post(
                f'https://graph.facebook.com/v21.0/486935574495266/messages', 
                headers=headers, 
                data=json.dumps(payload)
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception
        except Exception as e:
            return {'status': False, 'message': f'Oops, there was an error sending the message: {e}'}


    def send_message(self, message):
        try:
            headers = {
                'Authorization': f'Bearer {self.key}',
                'Content-Type': 'application/json'
            }

            payload = {
                'messaging_product': 'whatsapp',
                'to': message.phone_number,
                'type': 'text',
                'text': {
                    'body': message.text,
                }
            }
            response = requests.post(
                f'https://graph.facebook.com/v21.0/{message.phone_number_id}/messages', 
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
            url = f'https://graph.facebook.com/v21.0/{id}'
            
            headers = {
                'Authorization': f'Bearer {self.key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                media_data = response.json()
                return media_data['url']
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
        

    def convert_to_base64(self, file):
        try:
            return base64.b64encode(file).decode('utf-8')
        except Exception:
            return None


    def transcribe_audio(self, file):
        try:
            return openai_client.audio.transcriptions.create(model='whisper-v3', file=file).text
        except Exception:
            return None
        

    def upload_media(self, message, analysis_text):
        try:
            with open('analisis_semanal.txt', 'w', encoding='utf-8') as f:
                f.write(analysis_text)

            headers = {
                'Authorization': f'Bearer {self.key}'
            }

            files = {
            'file': ('analisis_semanal.txt', open('analisis_semanal.txt', 'rb'), 'text/plain')
        }

            response = requests.post(
                f'https://graph.facebook.com/v21.0/{message.phone_number_id}/media',
                data={
                    'messaging_product': 'whatsapp',
                    'type': 'text/plain'
                },
                files=files,
                headers=headers
            )

            if response.status_code == 200:
                media_data = response.json()
                return media_data['id']
            else:
                raise Exception(f"Upload failed: {response.text}")

        except Exception as e:
            return {'status': False, 'message': f'Error uploading analysis: {e}'}
        

    def send_media(self, message, media_id):
        try:
            headers = {
                'Authorization': f'Bearer {self.key}',
                'Content-Type': 'application/json'
            }

            payload = {
                'messaging_product': 'whatsapp',
                'recipient_type': 'individual',
                'to': message.phone_number,
                'type': 'document',
                'document': {
                    'id': media_id,
                    'caption': 'Análisis Semanal de Rendimiento Académico',
                    'filename': 'analisis_semanal.txt'
                }
            }

            response = requests.post(
                f'https://graph.facebook.com/v21.0/{message.phone_number_id}/messages',
                headers=headers,
                data=json.dumps(payload)
            )

            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Send failed: {response.text}")

        except Exception as e:
            return {'status': False, 'message': f'Error sending document: {e}'}