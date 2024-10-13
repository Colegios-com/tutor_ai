
import cohere
from cohere import ClassifyExample
import os


cohere_key = os.environ.get('COHERE_KEY')
cohere_client = cohere.Client(cohere_key)