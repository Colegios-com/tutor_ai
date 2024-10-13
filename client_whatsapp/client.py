import json
import random
import requests
import base64
import os

class WhatsappClient:
    def __init__(self, key):
        self.key = key

    def send_reaction(self, to, message_id, reaction):
        try:
            headers = {
                'Authorization': f'Bearer {self.key}',
                'Content-Type': 'application/json'
            }

            payload = {
                'messaging_product': 'whatsapp',
                'recipient_type': 'individual',
                'to': to,
                'type': 'reaction',
                'reaction': {
                    'message_id': message_id,
                    'emoji': reaction
                }
            }

            response = requests.post(
                'https://graph.facebook.com/v20.0/389338054272783/messages', 
                headers=headers, 
                data=json.dumps(payload)
            )
            if response.status_code == 200:
                return True
            else:
                raise Exception
        except Exception as e:
            print('Error reacting to message:', e)
            return {'status': False, 'message': f'Oops, there was an error sending the message: {e}'}

    def send_message(self, to, message):
        try:
            headers = {
                'Authorization': f'Bearer {self.key}',
                'Content-Type': 'application/json'
            }

            payload = {
                'messaging_product': 'whatsapp',
                'to': to,
                'type': 'text',
                'text': {
                    'body': message,
                }
            }
            response = requests.post(
                'https://graph.facebook.com/v20.0/389338054272783/messages', 
                headers=headers, 
                data=json.dumps(payload)
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception
        except Exception as e:
            return {'status': False, 'message': f'Oops, there was an error sending the message: {e}'}

    def get_media(self, media_id):
        try:
            url = f'https://graph.facebook.com/v20.0/{media_id}'
            
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

    def download_and_convert_to_base64(self, media_url):
        # Download the image            
        headers = {
            'Authorization': f'Bearer {self.key}',
            'Content-Type': 'application/json'
        }
        response = requests.get(media_url, headers=headers)
        if response.status_code == 200:
            # Get the content type and file extension
            content_type = response.headers.get('Content-Type', '')
            ext = content_type.split('/')[-1]
            
            # Save the image temporarily
            temp_filename = f'temp_image.{ext}'
            with open(temp_filename, 'wb') as f:
                f.write(response.content)
            
            # Read the image and convert to base64
            with open(temp_filename, 'rb') as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Remove the temporary file
            os.remove(temp_filename)
            
            return base64_image
        else:
            print(f'Error downloading image: {response.status_code}')
            return None