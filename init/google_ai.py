from google import genai
import os


google_key = os.getenv('GOOGLE_KEY')

google_client = genai.Client(api_key=google_key)
