import chromadb
import os

chroma_key = os.environ.get('CHROMA_KEY')


client = chromadb.CloudClient(
  api_key=chroma_key,
  tenant='7b7098df-b1b9-4400-a500-e3706360b27c',
  database='demo'
)