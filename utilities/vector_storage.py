from init.chroma import chroma_client
from init.cohere import cohere_client


collection = chroma_client.get_or_create_collection(name='colegios_tutor', metadata={'hnsw:space': 'cosine'})


def save_vectors(identifier: str, metadata: dict, data: list, embeddings: list):
    # Save
    result = collection.upsert(
        # List of Embeddings (Vectors)
        embeddings=embeddings,
        # List of corresponging Sources (String)
        documents=data,
        # List of unique IDs per Vector/String pair
        ids=[f'{identifier} {count}' for count, data_point in enumerate(data)],
        # Additional Metadata
        metadatas=[metadata for data_point in data],
    )
    return True


def get_vectors(workspace: str) -> list:
    return collection.get(where={'workspace': workspace})


def delete_vectors(id: str):
    try:
        collection.delete(where={'id': id})
        return True
    except:
        return False


def query_vectors(data: str, user: str) -> list:
    raw_embeddings = cohere_client.embed(texts=[data], model='embed-multilingual-v3.0', input_type='search_document')
    results = collection.query(
        query_embeddings=raw_embeddings.embeddings,
        where={'user': user},
        n_results=25,
    )
    # Extract all IDs
    documents = [document for document in results['documents'][0]]

    # Find the mode
    return documents