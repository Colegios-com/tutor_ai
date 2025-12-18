from datetime import datetime, timedelta, timezone
from data.models import Message
from init.supabase import supabase


def create_conversation(user_message: Message) -> str:
    """Creates a new conversation."""
    try:
        response = supabase.table("conversations").insert({"wa_id": user_message.wa_id, "bot_id": user_message.bot_id}).execute()
        return response.data[0]
    except Exception as e:
        return f"Error creating conversation: {str(e)}"


def get_active_conversation(user_message: Message) -> dict:
    """Simple helper to resolve phone number -> conversation_id and bot_id."""
    # get coversation no more than 10 minutes old
    now = datetime.now(timezone.utc)
    ten_minutes_ago = now - timedelta(minutes=10)
    conv = supabase.table("conversations").select("id, bots(id, restaurant_id)").eq("wa_id", user_message.wa_id).eq("status", "active").gte("updated_at", ten_minutes_ago).limit(1).execute()
    if conv.data:
        return conv.data[0]
    
    return {}


def add_messages(user_messages: list[Message]) -> None:
    """Saves messages to Supabase."""
    for user_message in user_messages:
        conversation = get_active_conversation(user_message)
        
        payload = {
            "phone_number_id": user_message.phone_number_id,
            "whatsapp_message_id": user_message.whatsapp_message_id,
            "wa_id": user_message.wa_id,
            "role": user_message.sender,
            "content": user_message.text,
            "message_type": user_message.message_type,
            "context": user_message.context,
            "file_metadata": {
                "uri": user_message.file.uri,
                "mime_type": user_message.file.mime_type,
            } if user_message.file else None,
        }
        if conversation:
            payload['conversation_id'] = conversation['id']

        supabase.table("messages").insert(payload).execute()


def get_message(whatsapp_message_id: str) -> Message | bool:
    """Gets a message by ID."""
    response = supabase.table("messages").select("*").eq("whatsapp_message_id", whatsapp_message_id).execute()
    if not response.data:
        return False
    return True


def build_conversation_history(user_message: Message) -> list[Message] | bool:
    """Gets all messages for a phone number."""
    conversation = get_active_conversation(user_message)

    if not conversation:
        print('No conversation found, send to bot router.')
        response = supabase.table("messages")\
            .select("*")\
            .eq("wa_id", user_message.wa_id)\
            .order("created_at", desc=False)\
            .execute()
    else:
        print('Conversation found, adding Conversation ID to message.')
        response = supabase.table("messages")\
            .select("*")\
            .eq("conversation_id", conversation['id'])\
            .order("created_at", desc=False)\
            .execute()

    if not response.data:
        print('No messages in conversation.')
        return []

    messages = []
    for row in response.data:
        messages.append(Message(
            id=row['id'],
            whatsapp_message_id=row['whatsapp_message_id'],
            phone_number_id=row['phone_number_id'],
            wa_id=user_message.wa_id,
            sender=row['role'],
            message_type=row.get('message_type', 'text'),
            text=row['content'],
            context=row.get('context'),
            file=row.get('file_metadata'),
            created_at=row['created_at'],
        ))
    
    return messages
