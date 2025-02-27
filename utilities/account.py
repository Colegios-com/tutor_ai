from utilities.storage import save_data, get_data

from data.models import Message

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, SendGridException, From


from datetime import datetime, timedelta
import os


def send_email(email: str, phone_number: str):
    sendgrid_key = os.environ.get('SENDGRID_KEY')

    welcomeMessage = Mail(
        from_email=From('bienvenido@colegios.com', 'Aldous 🖍️'),
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
    print(payload)
    # Payment Intent Success
    customer_id = payload['customer']['id']
    email = payload['customer']['email']
    name = payload['customer']['full_name']
    phone_number = payload['payment']['paymentable']['phone_number']
    striped_phone_number = phone_number.replace('+', '')

    # # Subscription Create
    # customer_id = payload['customer_id']
    # email = payload['customer_email']
    # name = payload['customer_name']
    # phone_number = payload['payment']['paymentable']['phone_number']
    # striped_phone_number = phone_number.replace('+', '')

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

    #TODO: Change from customer id to jwt(email).signature

    # Get or create user
    url = f'accounts/{customer_id}'
    user = get_data(url)

    if not user:
        user_data = {'email': email, 'name': name, 'phone_number': phone_number, 'customer_id': customer_id, 'subscription_type': subscription_type}
        save_data(url, user_data)

    
    # Calculate expiry date
    expiry_date = str(datetime.now() + timedelta(days=30))

    # Add subscription
    subscription_data = {'parent': email, 'subscription_type': subscription_type, 'usage': 0, 'tokens': 0, 'input_tokens': 0, 'output_tokens': 0, 'expiry_date': expiry_date}
    #TODO: Change from user id (instead of phone number) to jwt(phone).signature
    url = f'users/{striped_phone_number}/subscriptions/{transaction_id}'
    save_data(url, subscription_data)

    send_email(email=email, phone_number=phone_number)

    return phone_number


def verify_subscription(phone_number: str):
    # Gather data
    #TODO: Change from user id (instead of phone number) to jwt(phone).signature
    user_url = f'users/{phone_number}'
    user = get_data(user_url)

    if not user:
        # Add subscription
        expiry_date = str(datetime.now() + timedelta(days=7))
        subscription_data = {'subscription_type': 'starter', 'usage': 0, 'tokens': 0, 'input_tokens': 0, 'output_tokens': 0, 'expiry_date': expiry_date}
        url = f'users/{phone_number}/subscriptions/free_trial'
        save_data(url, subscription_data)
        return 'new_user'

    subscriptions_url = f'users/{phone_number}/subscriptions'
    subscription = get_data(subscriptions_url, order_by='expiry_date', limit=1)

    if subscription:
        _, subscription_data = subscription.popitem()
        expiry_date = datetime.strptime(subscription_data['expiry_date'], '%Y-%m-%d %H:%M:%S.%f')
        if datetime.now() < expiry_date:
            return subscription_data['subscription_type']

    return False


def update_usage(user_message: Message):
    # Gather data
    #TODO: Change from user id (instead of phone number) to jwt(phone).signature
    url = f'users/{user_message.phone_number}/subscriptions'
    subscription = get_data(url, order_by='expiry_date', limit=1)

    if subscription:
        subscription_id, subscription_data = subscription.popitem()
        subscription_data['usage'] += user_message.tokens
        subscription_data['tokens'] += user_message.tokens
        subscription_data['input_tokens'] += user_message.input_tokens
        subscription_data['output_tokens'] += user_message.output_tokens


        save_data(f'{url}/{subscription_id}', subscription_data)
