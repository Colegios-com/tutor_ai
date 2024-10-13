from firebase_admin import db
import json

def save_data(phone_number, message_dict):
    '''
    Save a message for a user identified by their phone number.
    
    :param phone_number: str, the user's phone number
    :param message_dict: dict, the message to be saved
    '''
    ref = db.reference(f'users/{phone_number}/messages')
    ref.push(message_dict)


def get_data(phone_number):
    '''
    Retrieve all messages for a user identified by their phone number.
    
    :param phone_number: str, the user's phone number
    :return: list of dictionaries, each representing a message
    '''
    ref = db.reference(f'users/{phone_number}/messages')
    messages = ref.get()
    return [msg for msg in messages.values()] if messages else []


def update_data(phone_number, message_id, updated_message_dict):
    '''
    Update a specific message for a user.
    
    :param phone_number: str, the user's phone number
    :param message_id: str, the ID of the message to update
    :param updated_message_dict: dict, the updated message content
    '''
    ref = db.reference(f'users/{phone_number}/messages/{message_id}')
    ref.update(updated_message_dict)


def delete_data(phone_number, message_id):
    '''
    Delete a specific message for a user.
    
    :param phone_number: str, the user's phone number
    :param message_id: str, the ID of the message to delete
    '''
    ref = db.reference(f'users/{phone_number}/messages/{message_id}')
    ref.delete()
