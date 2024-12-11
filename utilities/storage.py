from firebase_admin import db

test = False

def save_data(url, payload):
    '''
    Save a message for a user identified by their phone number.
    
    :param phone_number: str, the user's phone number
    :param message_dict: dict, the message to be saved
    '''
    if test:
        url = f'test/{url}'
        print('Test Mode')
    ref = db.reference(url)
    ref.set(payload)


def get_data(url):
    '''
    Retrieve all messages for a user identified by their phone number.
    
    :param phone_number: str, the user's phone number
    :return: list of dictionaries, each representing a message
    '''
    if test:
        url = f'test/{url}'
        print('Test Mode')
    ref = db.reference(url)
    return ref.get()


def update_data(url, payload):
    '''
    Update a message for a user identified by their phone number.
    
    :param phone_number: str, the user's phone number
    :param message_dict: dict, the message to be updated
    '''
    if test:
        url = f'test/{url}'
        print('Test Mode')
    ref = db.reference(url)
    ref.update(payload)


def delete_data(url):
    '''
    Delete all messages for a user identified by their phone number.
    
    :param phone_number: str, the user's phone number
    '''
    if test:
        url = f'test/{url}'
        print('Test Mode')
    ref = db.reference(url)
    ref.delete()
