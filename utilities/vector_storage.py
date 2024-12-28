from init.chroma import chroma_client
from init.cohere import cohere_client

import uuid
import time


collection = chroma_client.get_or_create_collection(name='colegios-ai', metadata={'hnsw:space': 'cosine'})


def save_vectors(metadata: dict, data: list, embeddings: list, identifier: str = None):
    if identifier is None:
        identifier = str(uuid.uuid4())

    metadata['timestamp'] = time.time()
    
    # Save
    result = collection.add(
        # List of Embeddings (Vectors)
        embeddings=embeddings,
        # List of corresponging Sources (String)
        documents=data,
        # List of unique IDs per Vector/String pair
        ids=[identifier for count, data_point in enumerate(data)],
        # Additional Metadata
        metadatas=[metadata for data_point in data],
    )
    print('Saving Vectors')
    return True


def get_vectors(user: str, context_type: str = None, timestamp: float = None) -> list:
    # Start with base condition for user
    conditions = [{'user': {'$eq': user}}]
    
    # Add context_type condition if provided
    if context_type is not None:
        conditions.append({'context_type': {'$eq': context_type}})
    
    # Add timestamp condition if date_range is provided
    if timestamp is not None:
        conditions.append({
            'timestamp': {
                '$gte': timestamp,
            }
        })
    
    # If only user condition exists, don't use $and
    metadata = {'$and': conditions} if len(conditions) > 1 else conditions[0]

    return collection.get(where=metadata)


def delete_vectors(id: str):
    try:
        collection.delete(where={'id': id})
        return True
    except:
        return False


def query_vectors(data: str, user: str, context_type: str = None, timestamp: float = None) -> list:
    # Start with base condition for user
    conditions = [{'user': {'$eq': user}}]
    
    # Add context_type condition if provided
    if context_type is not None:
        conditions.append({'context_type': {'$eq': context_type}})
    
    # Add timestamp condition if date_range is provided
    if timestamp is not None:
        conditions.append({
            'timestamp': {
                '$gte': timestamp,
            }
        })
    
    # If only user condition exists, don't use $and
    metadata = {'$and': conditions} if len(conditions) > 1 else conditions[0]

    raw_embeddings = cohere_client.embed(texts=[data], model='embed-multilingual-v3.0', input_type='search_document')
    results = collection.query(
        query_embeddings=raw_embeddings.embeddings,
        where=metadata,
        n_results=3,
    )
    documents = []
    for index, document in enumerate(results['documents'][0]):
        if results['distances'][0][index] < 0.4:
            documents.append(document)

    return documents
