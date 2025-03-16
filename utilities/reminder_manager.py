# Init
from init.whatsapp import whatsapp_client

# Utilities
from utilities.message_parser import build_agent_message, build_reminder_message
from utilities.response_orchestrator import orchestrate_reminder

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
    current_time = datetime.now()
    
    for user_id, user_data in users.items():
        # Skip if no last interaction data exists
        if not user_data or 'last_interaction' not in user_data:
            continue
            
        last_interaction = user_data['last_interaction']
        if not last_interaction or 'timestamp' not in last_interaction:
            continue
            
        # Convert timestamp to datetime
        last_timestamp = datetime.fromtimestamp(last_interaction['timestamp'])
        hours_since_interaction = (current_time - last_timestamp).total_seconds() / 3600
        
        # Determine which reminder type to send, if any
        reminder_type = should_send_reminder(user_id, hours_since_interaction, current_time)
        
        if reminder_type == "regular":
            # Regular reminder
            process_regular_reminder(user_data)
                
        elif reminder_type == "trial_expiration":
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
    orchestrate_reminder(user_message)
        

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
        "Tu prueba gratuita terminará pronto. ¡Invita a tus amigos y obtén una semana adicional por cada uno que se suscriba! Simplemente comparte el siguiente enlace con ellos 👇",
        f"¡Hola! 👋 Quiero invitarte a probar Aldous, ¡el tutor super inteligente que está revolucionando el aprendizaje! 🚀 Aldous te ayudará a entender CUALQUIER tema y a subir tus calificaciones. ¡Es como tener un genio a tu disposición! 🧠\n\n¡Pruébalo GRATIS! Al presionar el enlace de abajo y enviar el mensaje, ¡recibirás una semana ADICIONAL en tu prueba! 🎁 ¡No te lo pierdas! 👇\n\nhttps://api.whatsapp.com/send?phone=14243826945&text=Hola%20Aldous!%20Quiero%20activar%20mi%20prueba%20de%2014%20d%C3%ADas.%20Mi%20c%C3%B3digo%20es:%20%2A{user_message.phone_number}%2A"
    ]
    
    for message in messages:
        response_message = build_agent_message(user_message=user_message, raw_response=message)
        whatsapp_client.send_message(response_message=response_message)
        time.sleep(2)


def should_send_reminder(user_id, hours_since_interaction, current_time):
    """
    Determine which type of reminder to send, if any.
    Returns the reminder type ("regular", "trial_expiration") or None if no reminder should be sent.
    """
    # Determine reminder type based on time since last interaction
    if 12 <= hours_since_interaction < 13:
        return "regular"
    
    elif 22 <= hours_since_interaction < 23:
        # Check if user has a free trial subscription that will expire soon
        subscriptions_url = f'users/{user_id}/subscriptions'
        subscription = get_data(subscriptions_url, order_by='expiry_date', limit=1)
        
        if not subscription:
            return None
            
        subscription_id, subscription_data = subscription.popitem()
        
        if not subscription_id == 'free_trial':
            return None
            
        # Check if free trial ends in less than 24 hours
        expiry_date = datetime.strptime(subscription_data['expiry_date'], '%Y-%m-%d %H:%M:%S.%f')
        hours_until_expiry = (expiry_date - current_time).total_seconds() / 3600
        
        if not hours_until_expiry < 24:
            return None
            
        return "trial_expiration"
    return None 