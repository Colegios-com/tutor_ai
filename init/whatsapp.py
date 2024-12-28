from client_whatsapp.client import WhatsappClient
import os

whatsapp_key = os.environ.get('WHATSAPP_KEY')
whatsapp_client = WhatsappClient(key=whatsapp_key)
