from storage.storage import create_conversation

from init.supabase import supabase
from data.models import Message


# Default System Prompt Fallback
router_system_prompt = '''
    You are the point of entry for a food delivery aggregator via WhatsApp. Given the following tools, you must help the user get to the appropriate restaurant bot and help them with their request.

    Once you have successfully routed, your response message should mirror that of the bot's greeting message to show the user that you have successfully routed them to the appropriate bot. The restaurant name and description should be included in the response message.

    # Response Formatting
    ## 💬 Response Formatting for WhatsApp
    - **Indentation:** None (WhatsApp doesn't support it)
    - **Emphasis:** Use *bold* for important terms
    - **Numbers/Math/Code:** Wrap in `backticks`
    - **Vocabulary:** Use ```monospace```
    - **Examples:** Start with `>`
    - **Lists:** Use `-` and `1.`
    - **Emoji:** Use emoji
    - **No Tables/Nesting:** WhatsApp won't render them well
    - **Links:** Must be fully clickable URLs
'''


def get_bots(user_message: Message) -> str:
    """Helper to get the restaurant ID associated with the current BOT."""
    bot_list = supabase.table("bots").select("id, name, description, restaurants(id, name, description)").execute()
    if bot_list.data:
        return bot_list.data
    
    return "No bots found."


def route_user(user_message: Message, bot_id: str) -> str:
    user_message.bot_id = bot_id
    conversation = create_conversation(user_message)
    if conversation:
        bot = supabase.table("bots").select("id, name, description, personality, restaurants(name, description)").eq("id", bot_id).execute()
        if bot.data:
            return bot.data[0]
        return "Bot not found."
    
    return "Error creating conversation."



router_functions = {
    'get_bots': {
        'decalration': {
            'name': 'get_bots',
            'description': 'Use this to get a list of active service bots',
        },
        'function': get_bots,
    },
    'route_user': {
        'decalration': {
            'name': 'route_user',
            'description': 'Use this to route the user to the appropriate bot',
            'parameters': {
                'type': 'object',
                'properties': {
                    'bot_id': {'type': 'string'},
                },
                'required': ['bot_id'],
            },
        },
        'function': route_user,
    },
}