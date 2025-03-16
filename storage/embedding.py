from init.cohere import cohere_client


def embed_data(data: list) -> list:
    # Embed
    raw_embeddings = cohere_client.embed(texts=data, model='embed-multilingual-v3.0', input_type='search_document')
    return raw_embeddings.embeddings
