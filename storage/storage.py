from datetime import datetime
from data.models import Message
from init.supabase import supabase

BOT_ID = "1379630f-0437-41e1-9c03-82816b4768e0"


def _get_active_conversation_id(phone_number_id: str) -> str:
    """Simple helper to resolve phone number -> conversation_id."""
    # 1. Get Client
    client = supabase.table("clients").select("id").eq("phone", phone_number_id).maybe_single().execute()
    if not client:
        client = supabase.table("clients").insert({"phone": phone_number_id}).execute()
    client_id = client.data['id'] if 'id' in client.data else client.data[0]['id']

    # 2. Get Conversation
    conv = supabase.table("conversations").select("id").eq("client_id", client_id).eq("bot_id", BOT_ID).eq("status", "active").limit(1).execute()
    if conv.data:
        return conv.data[0]['id']
    
    # 3. Create if missing
    new_conv = supabase.table("conversations").insert({"bot_id": BOT_ID, "client_id": client_id, "status": "active"}).execute()
    return new_conv.data[0]['id']


def add_messages(new_messages: list[Message]) -> None:
    """Saves messages to Supabase."""
    for msg in new_messages:
        conversation_id = _get_active_conversation_id(msg.phone_number_id)
        
        payload = {
            "whatsapp_message_id": msg.whatsapp_message_id,
            "conversation_id": conversation_id,
            "role": msg.sender, # 'user' or 'model'
            "content": msg.text,
            "message_type": msg.message_type,
            "context": msg.context,
            "file_metadata": msg.file 
        }
        supabase.table("messages").insert(payload).execute()


def get_message(whatsapp_message_id: str) -> Message | bool:
    """Gets a message by ID."""
    response = supabase.table("messages").select("*").eq("whatsapp_message_id", whatsapp_message_id).execute()
    if not response.data:
        return False
    return True

def get_conversation(phone_number_id: str) -> list[Message] | bool:
    """Gets all messages for a phone number."""
    # 1. Find the conversation ID first
    # We can't query messages by phone directly because they are linked via conversation_id
    try:
        conversation_id = _get_active_conversation_id(phone_number_id)
    except:
        return False

    # 2. Fetch messages
    response = supabase.table("messages")\
        .select("*")\
        .eq("conversation_id", conversation_id)\
        .order("created_at", desc=False)\
        .execute()

    if not response.data:
        return False

    # 3. Map back to Message model
    messages = []
    for row in response.data:
        # Convert timestamp
        try:
            ts = datetime.fromisoformat(row['created_at'].replace('Z', '+00:00')).timestamp()
        except:
            ts = 0.0

        messages.append(Message(
            id=row['id'],
            whatsapp_message_id=row['whatsapp_message_id'],
            phone_number_id=phone_number_id,
            phone_number=phone_number_id,
            sender=row['role'],
            message_type=row.get('message_type', 'text'),
            text=row['content'],
            context=row.get('context'),
            file=row.get('file_metadata'),
            timestamp=ts
        ))
    
    return messages