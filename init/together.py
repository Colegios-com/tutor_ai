from client_together.client import TogetherAiClient
import os


together_key = os.environ.get('TOGETHER_KEY') or 'dc33c916632d4162ce27845814025a738dbc7ec99eaf6546434ab0d9d1bff57e'
together_client = TogetherAiClient(key=together_key)
