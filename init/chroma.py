from chromadb import CloudClient
import os

chroma_key = os.environ.get('CHROMA_KEY')
live = os.environ.get('LIVE') or False

database = 'colegios'
test_database = 'test-0d3eb34c'


chroma_client = CloudClient(
  tenant='7b7098df-b1b9-4400-a500-e3706360b27c',
  database=database if live else test_database,
  api_key=chroma_key,
  cloud_host='api.trychroma.com',
  cloud_port=8000,
  enable_ssl=True,
)
