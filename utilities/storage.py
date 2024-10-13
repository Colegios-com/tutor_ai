from init.chroma import chroma_client
from init.cohere import cohere_client

from statistics import mode


collection = chroma_client.get_or_create_collection(name='colegios_tutor', metadata={'hnsw:space': 'cosine'})


def save_data(template_id, descriptors, embeddings):
    # Save
    result = collection.upsert(
        # List of Embeddings (Vectors)
        embeddings=embeddings,
        # List of corresponging Sources (String)
        documents=descriptors,
        # List of unique IDs per Vector/String pair
        ids=[f'{template_id} {count}' for count, descriptor in enumerate(descriptors)],
        # Additional Metadata
        metadatas=[{'id': template_id} for descriptor in descriptors],
    )
    return True


def get_data(workspace: str) -> list:
    return collection.get(where={'workspace': workspace})


def delete_data(id: str):
    try:
        collection.delete(where={'id': id})
        return True
    except:
        return False


async def query_data(instruction: str) -> list:
    raw_embeddings = cohere_client.embed(texts=[instruction], model='embed-multilingual-v3.0', input_type='search_document')
    results = collection.query(
        query_embeddings=raw_embeddings.embeddings,
        n_results=10,
    )
    # Extract all IDs
    ids = [item['id'] for item in results['metadatas'][0]]

    # Find the mode
    template_id = mode(ids)
    return template_id