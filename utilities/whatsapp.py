from utilities.storage import save_data, get_data
from utilities.vector_storage import save_vectors, query_vectors
from utilities.embedding import embed_data


def save_message(message_id: str, phone_number: str, message_dict: dict, image_id: str = None):
    save_data(phone_number, message_dict)

    message = message_dict['image']['caption'] if image_id else message_dict['text']['body']

    embeddings = embed_data([message])
    
    metadata = {'user': phone_number}

    if image_id:
        metadata['image_id'] = image_id

    save_vectors(identifier=message_id, metadata=metadata, data=[message], embeddings=embeddings)


def get_messages(phone_number: str, message: str):
    messages = get_data(phone_number)
    vectors = query_vectors(data=message, user=phone_number)
    messages = [f'{"Agent" if message["from"] == "agent" else "User"} (sent at {message["timestamp"]}): {message["image"]["caption"] if message["type"] == "image" else message["text"]["body"]}' for message in messages]
    return {'messages': messages[-15:], 'vectors': vectors}
