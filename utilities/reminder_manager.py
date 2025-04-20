# Init
from init.whatsapp import whatsapp_client

# Utilities
from utilities.message_parser import build_agent_message, build_reminder_message
from utilities.response_orchestrator import orchestrate_reminder
from utilities.usage import update_messages, update_last_interaction

# Storage
from storage.storage import get_data

# Standard
from datetime import datetime
import time

def process_reminders():
    """
    Process all types of reminders for users based on their last interaction time.
    Returns the number of reminders sent.
    """
    users = get_data('users')
    
    for _, user_data in users.items():

        # if _ != '16466219257':
        #     continue

        # Skip if no last interaction data exists
        if not user_data or 'last_interaction' not in user_data:
            continue
            
        last_interaction = user_data['last_interaction']
        if not last_interaction or 'timestamp' not in last_interaction:
            continue
            
        # Convert timestamp to datetime
        last_timestamp = float(last_interaction['timestamp'])
        current_timestamp = time.time()
        hours_since_interaction = (current_timestamp - last_timestamp) / 3600
        
        # Determine which reminder type to send, if any
        reminder_type = should_send_reminder(user_data, hours_since_interaction, current_timestamp)
        
        if reminder_type == 'regular':
            # Regular reminder
            process_regular_reminder(user_data)
                
        elif reminder_type == 'trial_expiration':
            # Trial expiration reminder
            process_trial_expiration_reminder(user_data)

    return True


def process_regular_reminder(user_data):
    """
    Process regular reminders for users who haven't interacted in 12-13 hours.
    Returns True if a reminder was sent, False otherwise.
    """
    # Create user message for the reminder
    user_message = build_reminder_message(user_data)
    if not user_message:
        return False
            
    # Regular reminder with agent-generated content
    response_message, response = orchestrate_reminder(user_message)
    if not response_message or not response:
        return False
            
    response_message.id = response['messages'][0]['id'].replace('wamid.', '')

    update_messages([response_message])
    update_last_interaction(response_message=response_message)

    return True
        

def process_trial_expiration_reminder(user_data):
    """
    Process reminders for users on free trials that are about to expire.
    Returns True if a reminder was sent, False otherwise.
    """
    # Create user message for the reminder
    user_message = build_reminder_message(user_data)
    if not user_message:
        return False
        
    # Trial expiration reminder with referral link
    messages = [
        'Tu prueba gratuita terminará pronto. ¡Invita a tus amigos y obtén una semana adicional por cada uno que se suscriba! Simplemente comparte el siguiente enlace con ellos',
        f'¡Hola! 👋 Quiero invitarte a probar Aldous, ¡el tutor super inteligente que está revolucionando el aprendizaje! 🚀 Aldous te ayudará a entender CUALQUIER tema y a subir tus calificaciones. ¡Es como tener un genio a tu disposición! 🧠\n\n¡Pruébalo GRATIS! Al presionar el enlace de abajo y enviar el mensaje, ¡recibirás una semana ADICIONAL en tu prueba! 🎁 ¡No te lo pierdas! 👇\n\nhttps://api.whatsapp.com/send?phone=14243826945&text=Hola%20Aldous!%20Quiero%20activar%20mi%20prueba%20de%2014%20d%C3%ADas.%20Mi%20c%C3%B3digo%20es:%20%2A{user_message.phone_number}%2A',
    ]
    
    for message in messages:
        response_message = build_agent_message(user_message=user_message, raw_response=message)
        response = whatsapp_client.send_message(response_message=response_message)
        response_message.id = response['messages'][0]['id'].replace('wamid.', '')
        update_messages([response_message])
        time.sleep(2)
    
    update_last_interaction(response_message=response_message)

    return True


def should_send_reminder(user_data, hours_since_interaction, current_timestamp):
    """
    Determine which type of reminder to send, if any.
    Returns the reminder type ("regular", "trial_expiration") or None if no reminder should be sent.
    """
    subscriptions = user_data.get('subscriptions', {})
    if not subscriptions:
        return None
        
    # Find the subscription with the latest expiry date
    latest_subscription = max(subscriptions.values(), key=lambda x: x.get('expiry_date', 0))
    
    if not latest_subscription:
        return None
        
    # Check if subscription has expired
    expiry_date = datetime.strptime(latest_subscription['expiry_date'], '%Y-%m-%d %H:%M:%S.%f')
    if expiry_date < datetime.now():
        return None
    
    # Determine reminder type based on time since last interaction
    if 4 <= hours_since_interaction < 5:
        # Send regular reminder after 4-5 hours of inactivity
        return 'regular'
    elif 22 <= hours_since_interaction < 23:
        # Check specifically for free trial expiration
        subscription_id = next(iter(latest_subscription), None)
        
        # Only proceed if this is a free trial
        if subscription_id != 'free_trial':
            return None
            
        # Calculate hours until expiry
        hours_until_expiry = (expiry_date - current_timestamp) / 3600
        
        # Send trial expiration reminder if less than 24 hours remain
        if hours_until_expiry < 24:
            return 'trial_expiration'
            
        return None
    else:
        return None