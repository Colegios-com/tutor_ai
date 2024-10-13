from chromadb import HttpClient
import os

chroma_key = os.environ.get('CHROMA_KEY') or 'ck-8QXLN8d2FVhtCF8Wg5dPSh9x9gyWAMyGguvjytE5xMiE'

chroma_client = HttpClient(
  ssl=True,
  host='api.trychroma.com',
  tenant='7b7098df-b1b9-4400-a500-e3706360b27c',
  database='colegios',
  headers={
      'x-chroma-token': chroma_key
  }
)