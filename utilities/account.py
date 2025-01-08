from utilities.storage import save_data, get_data

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, SendGridException, From


from datetime import datetime, timedelta
import os


def send_email(email: str, phone_number: str):
    sendgrid_key = os.environ.get('SENDGRID_KEY')

    welcomeMessage = Mail(
        from_email=From('bienvenido@colegios.com', 'Colegios.com'),
        to_emails=email,
        subject='Comienza Ahora 📝',
    )
    welcomeMessage.template_id = 'd-43fae76bfca747b4bf81f01bf6df01fa'
    welcomeMessage.dynamic_template_data = {
        'phone': phone_number,
    }
    try:
        email = SendGridAPIClient(sendgrid_key)
        email.send(welcomeMessage)
    except SendGridException as e:
        print(e)


def save_user(payload: dict):
    # Gather data
    customer_id = payload['customer']['id']
    email = payload['customer']['email']
    name = payload['customer']['full_name']
    phone_number = payload['payment']['paymentable']['phone_number']
    striped_phone_number = phone_number.replace('+', '')

    # Build subscription data
    transaction_id = payload['id']
    product_id = payload['product']['id']
    if product_id == 'prod_xnyjtgvv':
        subscription_type = 'unlimited'
    elif product_id == 'prod_mvalkv9n':
        subscription_type = 'pro'
    elif product_id == 'prod_9qyu5yj0':
        subscription_type = 'tester'
    else:
        subscription_type = 'starter'

    # Get or create user
    url = f'accounts/{customer_id}'
    user = get_data(url)

    if not user:
        user_data = {'email': email, 'name': name, 'phone_number': phone_number, 'customer_id': customer_id, 'subscription_type': subscription_type}
        save_data(url, user_data)

    
    # Calculate expiry date
    expiry_date = str(datetime.now() + timedelta(days=30))

    # Add subscription
    subscription_data = {'parent': email, 'subscription_type': subscription_type, 'usage': 0, 'expiry_date': expiry_date}
    url = f'users/{striped_phone_number}/subscriptions/{transaction_id}'
    save_data(url, subscription_data)

    send_email(email=email, phone_number=phone_number)

    return phone_number


def verify_subscription(phone_number: str):
    # Gather data
    url = f'users/{phone_number}/subscriptions'
    subscriptions = get_data(url)

    if subscriptions:
        for subscription in subscriptions.values():
            expiry_date = datetime.strptime(subscription['expiry_date'], '%Y-%m-%d %H:%M:%S.%f')
            if datetime.now() < expiry_date:
                return subscription['subscription_type']

    return False


def verify_access(phone_number: str):
    # Gather data
    url = f'users/{phone_number}/subscriptions'
    subscriptions = get_data(url)

    if subscriptions:
        for subscription in subscriptions.values():
            type = subscription['subscription_type']
            if type == 'admin':
                return True

    return False
