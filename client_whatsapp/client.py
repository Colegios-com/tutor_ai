from init.openai import openai_client

import requests
import base64
import json


class WhatsappClient:
    def __init__(self, key):
        self.key = key

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
            print(response.text)
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
            return {'status': False, 'message': f'Oops, there was an error sending the message: {e}'}

    def get_media(self, id):
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
        
    def upload_media(self, message) -> dict:
        try:
            with open('analisis_semanal.txt', 'w', encoding='utf-8') as f:
                analysis_text = '''Análisis de Rendimiento Académico - Enfoque RTI Finlandés\nEstudiante: Enrique\nPeríodo: Últimos 7 días\n\n📊 RESUMEN EJECUTIVO\nEnrique muestra un patrón de aprendizaje que requiere atención personalizada en áreas específicas, manteniendo fortalezas notables en otras. Siguiendo el modelo finlandés de intervención temprana, hemos identificado oportunidades de apoyo inmediato.\n\n💪 FORTALEZAS\n- Excelente participación en discusiones grupales\n- Alta creatividad en resolución de problemas\n- Fuerte capacidad de análisis verbal\n\n🎯 ÁREAS DE ATENCIÓN\n- Organización del tiempo en tareas escritas\n- Consistencia en ejercicios matemáticos básicos\n- Atención sostenida en lecturas largas\n\n📈 PLAN DE INTERVENCIÓN PROPUESTO\nNivel 1 (Apoyo General):\n- Mantener rutinas estructuradas de estudio\n- Implementar pausas activas cada 25 minutos\n- Usar recursos visuales para conceptos abstractos\n\nNivel 2 (Apoyo Focalizado):\n- Sesiones individuales de 20 minutos en matemáticas\n- Ejercicios de comprensión lectora guiada\n- Herramientas de organización personal\n\n🤝 RECOMENDACIONES\nPara Padres:\n- Establecer horarios fijos de estudio\n- Reforzar positivamente los logros pequeños\n- Mantener comunicación regular con tutores\n\nPara Docentes:\n- Proporcionar instrucciones paso a paso\n- Permitir tiempo extra en evaluaciones escritas\n- Implementar evaluación continua\n\nPara Enrique:\n- Utilizar agenda digital/física para organización\n- Practicar técnicas de auto-monitoreo\n- Comunicar dudas inmediatamente\n\n🌟 PRONÓSTICO\nCon la implementación consistente de estas estrategias, esperamos ver mejoras significativas en 3-4 semanas, especialmente en organización y matemáticas básicas.'''
                f.write(analysis_text)

            headers = {
                'Authorization': f'Bearer {self.key}'
            }

            files = {
            'file': ('analisis_semanal.txt', open('analisis_semanal.txt', 'rb'), 'text/plain', {'Expires': '0'})
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
        

    def send_media(self, message, media_id: str) -> dict:
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
                    'caption': 'Análisis de Rendimiento Académico - Enrique',
                    'filename': 'analisis_enrique.txt'
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