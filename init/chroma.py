from chromadb import HttpClient
import os

chroma_key = os.environ.get('CHROMA_KEY')
live = os.environ.get('LIVE') or False

database = 'colegios'
test_database = 'test-0d3eb34c'

chroma_client = HttpClient(
  ssl=True,
  host='api.trychroma.com',
  tenant='7b7098df-b1b9-4400-a500-e3706360b27c',
  database=database if live else test_database,
  headers={
      'x-chroma-token': chroma_key
  }
)