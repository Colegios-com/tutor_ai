from utilities.storage import save_data, get_data
from datetime import datetime, timedelta


def save_user(payload: dict):
    # Gather data
    customer_id = payload['customer_id']
    email = payload['customer']['email']
    name = payload['customer']['full_name']
    phone_number = payload['payment']['paymentable']['phone_number']
    striped_phone_number = phone_number.replace('+', '')

    # Get or create user
    user_data = {'email': email, 'name': name, 'phone_number': phone_number, 'customer_id': customer_id}
    url = f'accounts/{striped_phone_number}'
    user = get_data(url)

    if not user:
        save_data(url, user_data)

    
    # Calculate expiry date
    expiry_date = str(datetime.now() + timedelta(days=30))

    # Build subscription data
    transaction_id = payload['id']
    product_id = payload['product']['id']
    if product_id == 'abc_123':
        product_type = 'ultimate'
    elif product_id == 'xyz_123':
        product_type = 'boster'
    else:
        product_type = 'starter'

    # Add subscription
    subscription_data = {'type': product_type, 'usage': 0, 'expiry_date': expiry_date}
    url = f'users/{striped_phone_number}/subscriptions/{transaction_id}'
    save_data(url, subscription_data)

    return phone_number


def verify_subscription(phone_number: str):
    # Gather data
    url = f'users/{phone_number}/subscriptions'
    subscriptions = get_data(url)

    if subscriptions:
        for subscription in subscriptions.values():
            expiry_date = datetime.strptime(subscription['expiry_date'], '%Y-%m-%d %H:%M:%S.%f')
            if datetime.now() < expiry_date:
                return True

    return False


def verify_access(phone_number: str):
    # Gather data
    url = f'users/{phone_number}/subscriptions'
    subscriptions = get_data(url)

    if subscriptions:
        for subscription in subscriptions.values():
            type = subscription['type']
            if type == 'admin':
                return True

    return False