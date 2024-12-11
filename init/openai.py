import openai
import os


fireworls_key = os.getenv('FIREWORKS_KEY') or 'fw_3ZaRzYg8W6YC9AH19Jmc3gTp'

openai_client = openai.OpenAI(
    base_url='https://api.fireworks.ai/inference/v1',
    api_key=fireworls_key,
)
