# Storage
from storage.storage import save_data, get_data, update_data
from storage.embedding import embed_data
from storage.vector_storage import save_vectors

# Data
from data.models import Message


def update_memories(memory_text, user_message):
    """
    Save memory text as vector embeddings in the database.
    
    Args:
        memory_text (str): The memory text to be embedded and saved
        user_message (Message): The user's message object
    """
    embeddings = embed_data([memory_text])
    metadata = {'user': user_message.phone_number, 'context_type': 'general'}

    if user_message.media_id:
        metadata['media_id'] = user_message.media_id

    save_vectors(metadata=metadata, data=[memory_text], embeddings=embeddings)


def update_messages(messages: list[Message]):
    """
    Store message data in the database.
    
    Args:
        user_message (Message): The user's message object
        response_message (Message): The response message object
    """
    for message in messages:
        message_url = f'users/{message.phone_number}/messages/{message.id.replace("wamid.", "")}'
        save_data(message_url, message.dict())


def update_last_interaction(user_message=None, response_message=None):
    """
    Update the last interaction data for a user in the database.
    
    Args:
        user_message (Message): The user's message object
        response_message (Message): The response message object
    """
    last_interaction_url = f'users/{user_message.phone_number}/last_interaction' if user_message else f'users/{response_message.phone_number}/last_interaction'
    payload = {}
    if user_message:
        payload['timestamp'] = user_message.timestamp
        payload['user_message'] = user_message.dict()
    if response_message:
        payload['response_message'] = response_message.dict()
    update_data(last_interaction_url, payload)


def update_usage(user_message: Message):
    # Gather data
    url = f'users/{user_message.phone_number}/subscriptions'
    subscription = get_data(url, order_by='expiry_date', limit=1)

    if subscription:
        subscription_id, subscription_data = subscription.popitem()
        subscription_data['usage'] += user_message.tokens
        subscription_data['tokens'] += user_message.tokens
        subscription_data['input_tokens'] += user_message.input_tokens
        subscription_data['output_tokens'] += user_message.output_tokens

        save_data(f'{url}/{subscription_id}', subscription_data)