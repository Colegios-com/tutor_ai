# Init
from init.whatsapp import whatsapp_client

# Utilities
from utilities.message_parser import build_agent_message
from utilities.authentication import sign
from utilities.usage import update_messages, update_last_interaction
# Storage
from storage.storage import save_data, update_data, get_data

# Data
from data.models import Message

# SendGrid
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, SendGridException, From

# Standard
from datetime import datetime, timedelta
import os
import time
import re

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


def create_subscription(payload: dict):
    # Payment Intent Success
    customer_id = payload['customer']['id']
    customer_email = payload['customer']['email']
    customer_name = payload['customer']['full_name']
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

    
    # Calculate expiry date
    expiry_date = str(datetime.now() + timedelta(days=30))

    # Add subscription
    subscription_data = {'customer_id': customer_id, 'customer_name': customer_name, 'email': customer_email, 'subscription_type': subscription_type, 'usage': 0, 'tokens': 0, 'input_tokens': 0, 'output_tokens': 0, 'expiry_date': expiry_date}
    url = f'users/{striped_phone_number}/subscriptions/{transaction_id}'
    save_data(url, subscription_data)

    send_email(email=customer_email, phone_number=phone_number)

    return phone_number


def handle_referral(referrer_phone: str, referral_phone: str):
    # Check if free trial exists
    subscription_url = f'users/{referrer_phone}/subscriptions/free_trial'
    existing_subscription = get_data(subscription_url)
    
    # Add or update subscription
    if existing_subscription:
        # Check if subscription is expired
        current_expiry = datetime.strptime(existing_subscription['expiry_date'], '%Y-%m-%d %H:%M:%S.%f')
        if datetime.now() > current_expiry:
            # Subscription expired, add 7 days from now
            expiry_date = str(datetime.now() + timedelta(days=7))
        else:
            # Subscription still active, add 7 days to current expiry date
            expiry_date = str(current_expiry + timedelta(days=7))
        
        subscription_data = {'expiry_date': expiry_date}
        update_data(subscription_url, subscription_data)

        referral_url = f'users/{referrer_phone}/referrals/{referral_phone}'
        referral_data = {'timestamp': str(datetime.now())}
        save_data(referral_url, referral_data)
        return True
    else:
        return False
    

def create_free_trial(user_message: Message):
    # Default trial configuration
    default_config = {
        'trial_days': 7,
        'subscription_type': 'pro',
        'onboarding': 'General Help',
    }
    # Define special codes with their configurations
    SPECIAL_CODES = {
        'H9': {
            'trial_days': 7,
            'subscription_type': 'pro',
            'onboarding': 'Homework Helper',
        },
        'E2': {
            'trial_days': 7,
            'subscription_type': 'pro',
            'onboarding': 'Exam Prep',
        },
        'L4': {
            'trial_days': 14,
            'subscription_type': 'pro',
            'onboarding': 'Better Learning',
        },
        'G3': {
            'trial_days': 14,
            'subscription_type': 'pro',
            'onboarding': 'Grade Improvement',
        },
    }
    
    # Get trial configuration based on special code
    config = default_config.copy()
    special_code_match = re.search(r"\*(.*?)\*", user_message.text)
    
    if special_code_match:
        special_code = special_code_match.group(1)
        
        if special_code in SPECIAL_CODES:
            # Use predefined special code configuration
            config.update(SPECIAL_CODES[special_code])
        else:
            # Check if it's a referral code (assume it's a phone number)
            if handle_referral(special_code, user_message.phone_number):
                config.update({
                    'trial_days': 14,
                    'onboarding': f'Referral Code: {special_code}',
                })
    
    # Create subscription
    timestamp = datetime.now()
    expiry_date = str(timestamp + timedelta(days=config['trial_days']))
    
    subscription_data = {
        'subscription_type': config['subscription_type'],
        'usage': 0,
        'tokens': 0,
        'input_tokens': 0,
        'output_tokens': 0,
        'start_date': str(timestamp),
        'expiry_date': expiry_date,
        'onboarding': config['onboarding'],
    }

    # Save subscription data
    url = f'users/{user_message.phone_number}/subscriptions/free_trial'
    save_data(url, subscription_data)
    update_messages([user_message])

    # Send welcome messages
    welcome_messages = [
        {
            'message': f'*¡Hola! 👋 Soy Aldous, tu tutor académico personal*\n\nTu prueba de {config["trial_days"]} días está activa. Estoy aquí para:\n\n• *Resolver dudas académicas* 🧠\n• *Explicar conceptos difíciles* 📚\n• *Ayudarte con tareas* ✏️',
            'type': 'image'
        },
        {
            'message': '*Para obtener mejores resultados:*\n\n1️⃣ Sé específico en tus preguntas\n2️⃣ Incluye contexto relevante\n3️⃣ Explica lo que ya entiendes\n\n*¿En qué puedo ayudarte hoy? Prueba:*\n\n`Escribir tu primera consulta detallada ✏️`\n`Enviar una foto de tu tarea 📸`\n`Grabar un mensaje 🎤`',
            'type': 'text'
        },
    ]
    
    # Send each welcome message
    for message in welcome_messages:
        if message['type'] == 'image':
            with open(f'images/aldous.png', 'rb') as file:
                file_content = file.read()
                media_id = whatsapp_client.upload_media(message=user_message, file_content=file_content, file_name='image.png', file_type='image/png')        
            
            response_message = build_agent_message(user_message=user_message, raw_response=message['message'], message_type='text', media_id=media_id)
            response =whatsapp_client.send_media(message=response_message, media_id=response_message.media_id, file_name='image.png', file_type='image', caption=message['message'])
        else:
            response_message = build_agent_message(user_message=user_message, raw_response=message['message'])
            response = whatsapp_client.send_message(response_message=response_message)
        
        time.sleep(2)
        response_message.id = response['messages'][0]['id'].replace('wamid.', '')
        update_messages([response_message])

    update_last_interaction(user_message, response_message)
    

    # Send celebration reaction
    whatsapp_client.send_reaction(user_message=user_message, reaction='🎉')


def verify_user(user_message: Message):
    # Gather data
    user_url = f'users/{user_message.phone_number}'
    user = get_data(user_url)

    if not user:
        # Add subscription
        create_free_trial(user_message)
        return False
    
    return True


def verify_subscription(user_message: Message):
    subscriptions_url = f'users/{user_message.phone_number}/subscriptions'
    subscription = get_data(subscriptions_url, order_by='expiry_date', limit=1)

    if not subscription:
        raw_response = '¡No dejes que tus estudios se queden atrás! Reactiva tu suscripción a Aldous y ten a mano ayuda experta, disponible cuando la necesites. ¡Es fácil y rápido! 🚀\n\n👉 https://app.recurrente.com/s/colegios-com/plan-pro'
        response_message = build_agent_message(user_message=user_message, raw_response=raw_response)
        whatsapp_client.send_message(response_message=response_message)
        whatsapp_client.send_reaction(user_message=user_message, reaction='💸')
        return False

    subscription_id, subscription_data = subscription.popitem()
    now = datetime.now()
    expiry_date = datetime.strptime(subscription_data['expiry_date'], '%Y-%m-%d %H:%M:%S.%f')

    if now > expiry_date:
        messages = [
            "*Tu suscripción ha expirado*.\n\n¡Invita a tus amigos y obtén una semana adicional de uso gratis por cada uno que se suscriba! Simplemente comparte el siguiente enlace con ellos.",
            f"¡Hola! 👋 Quiero invitarte a probar Aldous, ¡el tutor super inteligente que está revolucionando el aprendizaje! 🚀 Aldous te ayudará a entender CUALQUIER tema y a subir tus calificaciones. ¡Es como tener un genio a tu disposición! 🧠\n\n¡Pruébalo GRATIS! Al presionar el enlace de abajo y enviar el mensaje, ¡recibirás una semana ADICIONAL en tu prueba! 🎁 ¡No te lo pierdas! 👇\n\nhttps://api.whatsapp.com/send?phone=14243826945&text=Hola%20Aldous!%20Quiero%20activar%20mi%20prueba%20de%2014%20d%C3%ADas.%20Mi%20c%C3%B3digo%20es:%20%2A{user_message.phone_number}%2A"
        ]
        
        for message in messages:
            response_message = build_agent_message(user_message=user_message, raw_response=message)
            whatsapp_client.send_message(response_message=response_message)
            time.sleep(2)
        
        whatsapp_client.send_reaction(user_message=user_message, reaction='🎁')
        return False

    # If subscription is free_trial, check if user has a profile
    if subscription_id == 'free_trial':
        intake_data = get_data(f'users/{user_message.phone_number}/profile')
        if not intake_data and now > expiry_date - timedelta(days=3):
            raw_response = f'Psst, debes aceptar los términos y condiciones para continuar.\n\nhttps://aldous.colegios.com/intake/{sign(user_message.phone_number)}/'
            response_message = build_agent_message(user_message=user_message, raw_response=raw_response)
            whatsapp_client.send_message(response_message=response_message)
            whatsapp_client.send_reaction(user_message=user_message, reaction='📝')
            return False
        
    return subscription_data['subscription_type']        
