from init.supabase import supabase

from data.models import Message


# ==========================================
# 2. SYSTEM PROMPT GENERATION (UNCHANGED)
# ==========================================


# Default System Prompt Fallback
system_prompt = '''You are a freindly bot that helps with customer service.''' 


FORMATTING_RULES = '''
    # Response Formatting
    ## 💬 Response Formatting for WhatsApp
    - **Indentation:** None (WhatsApp doesn't support it)
    - **Emphasis:** Use *bold* for important terms
    - **Numbers/Math/Code:** Wrap in `backticks`
    - **Vocabulary:** Use ```monospace```
    - **Examples:** Start with `>`
    - **Lists:** Use `-` and `1.`
    - **Emoji:** {emoji_instruction}
    - **No Tables/Nesting:** WhatsApp won't render them well
    - **Links:** Must be fully clickable URLs
'''


def _generate_mermaid_graph(flow_data: dict) -> str:
    if not flow_data or 'nodes' not in flow_data or 'edges' not in flow_data:
        return ""
    mermaid_lines = ["# Workflow", "Follow this logic flow strictly:", "graph TD"]
    for node in flow_data['nodes']:
        n_id = node['id']
        n_label = node['data'].get('label', 'Action')
        n_type = node.get('type', 'default')
        if n_type == 'condition':
            mermaid_lines.append(f'    {n_id}{{{n_label}}}')
        elif n_type == 'start':
            mermaid_lines.append(f'    {n_id}(({n_label}))')
        elif n_type == 'end':
            mermaid_lines.append(f'    {n_id}(({n_label}))')
        else:
            mermaid_lines.append(f'    {n_id}[{n_label}]')
    for edge in flow_data['edges']:
        source = edge['source']
        target = edge['target']
        label = edge.get('label') or edge.get('source_handle')
        if label:
            clean_label = label.capitalize()
            mermaid_lines.append(f'    {source} -->|{clean_label}| {target}')
        else:
            mermaid_lines.append(f'    {source} --> {target}')
    return "\n".join(mermaid_lines)


def _interpret_personality(personality: dict) -> tuple[str, str]:
    emoji_score = personality.get('emoji_usage', 50)
    if emoji_score < 30:
        emoji_inst = "Do not use emojis."
    elif emoji_score < 70:
        emoji_inst = "Use emojis sparingly and only for encouragement (👍, ✨)."
    else:
        emoji_inst = "Use emojis frequently to create a very lively atmosphere."

    formality = personality.get('formality', 50)
    tone_base = personality.get('tone', 'neutral')
    if formality > 70:
        tone_inst = f"Maintain a strictly formal and professional {tone_base} tone."
    elif formality < 30:
        tone_inst = f"Maintain a very casual, slang-friendly {tone_base} tone."
    else:
        tone_inst = f"Maintain a balanced, polite {tone_base} tone."
    return emoji_inst, tone_inst


def _get_upselling_instructions(config: dict) -> str:
    if not config.get('enabled', False):
        return ""
    techniques = config.get('techniques', {})
    active_techniques = [k.replace('_', ' ').title() for k, v in techniques.items() if v]
    aggressiveness = config.get('aggressiveness', 50)
    frequency = "occasionally" if aggressiveness < 50 else "aggressively"
    return f"""
    ## Upselling Strategy
    - You are instructed to {frequency} suggest additional items.
    - Suggest items after every {config.get('suggest_after_items', 1)} item(s) added by the user.
    - Max suggestions per conversation: {config.get('max_suggestions_per_conversation', 3)}.
    - Focus on these techniques: {', '.join(active_techniques)}.
    """


def get_system_prompt(user_message: Message) -> str:
    response = supabase.table("bots").select("*").eq("id", user_message.bot_id).single().execute()
    if not response:
        return system_prompt # Return default if DB fails

    bot_config = response.data
    name = bot_config.get('name', 'Assistant')
    description = bot_config.get('description', 'A helpful bot.')
    personality = bot_config.get('personality', {})
    upselling = bot_config.get('upselling_config', {})
    flow_graph = bot_config.get('flow_graph', {})
    
    emoji_instruction, tone_instruction = _interpret_personality(personality)
    upselling_instruction = _get_upselling_instructions(upselling)
    mermaid_graph = _generate_mermaid_graph(flow_graph)
    core_persona = personality.get('system_prompt', description)

    composed_system_prompt = f'''
    You are **{name}**. {core_persona}
    
    ## Objective
    {description}

    ## Personality & Tone
    - {tone_instruction}

    ## Strictly follow the following instructions

    - For the first greeting, use: "{personality.get('greeting', 'Hello!')}".
    - Once the conversation ends, use: "{personality.get('farewell', 'Goodbye!')}".
    - The response language should be {personality.get('language', 'the same as the incoming message language')}.
    - Aim for a length score of {personality.get('response_length', 50)}/100.

    {upselling_instruction}

    {mermaid_graph}

    {FORMATTING_RULES.format(emoji_instruction=emoji_instruction)}
    '''
    return composed_system_prompt


# ==========================================
# CONVERSATION MANAGEMENT
# ==========================================


def get_bots(user_message: Message) -> list[dict]:
    """
    Returns a list of bots for the restaurant.
    """
    try:
        response = supabase.table("bots").select("id, name, description").eq("restaurant_id", user_message.restaurant_id).execute()
        return response.data
    except Exception as e:
        return f"Error getting bots: {str(e)}"


def transfer_conversation(user_message: Message, bot_id: str | None = None) -> str:
    """
    Transfers the conversation to a different bot.
    """
    if not bot_id:
        return end_conversation(user_message)
    
    try:
        updated_conversation = supabase.table("conversations").update({"bot_id": bot_id}).eq("id", user_message.conversation_id).execute()
        if updated_conversation.data:
            return f"The conversation has been transferred to bot {bot_id}."
        return "Conversation ID not found."
    except Exception as e:
        return f"Error transferring conversation: {str(e)}"


def end_conversation(user_message: Message) -> str:
    """
    Ends the conversation.
    """
    try:
        updated_conversation = supabase.table("conversations").update({"status": "closed"}).eq("id", user_message.conversation_id).execute()
        if updated_conversation.data:
            return "The conversation has ended."
        return "Conversation ID not found."
    except Exception as e:
        return f"Error ending conversation: {str(e)}"


# ==========================================
# RESTAURANT INFORMATION
# ==========================================


def answer_faq(user_message: Message) -> str:
    """
    Returns text containing all FAQs for the restaurant.
    """
    try:
        response = supabase.table("faqs").select("question, answer").eq("restaurant_id", user_message.restaurant_id).execute()
        
        if not response:
            return "No FAQ information is currently available."

        return response.data
    except Exception as e:
        return f"Error retrieving FAQs: {str(e)}"


def get_menu(user_message: Message) -> str:
    """
    Returns the menu items list.
    """
    try:
        response = supabase.table("menus").select("id, name, type, menu_items(id, name, description, price)").eq("restaurant_id", user_message.restaurant_id).execute()
        if not response:
            return "No menu information is currently available."
            
        return response.data
    except Exception as e:
        return f"Error retrieving menu: {str(e)}"


def get_promotions(user_message: Message) -> str:
    """
    Returns the promotions list.
    """
    try:
        response = supabase.table("promotions").select("id, name, tag, description, bot_instruction").eq("restaurant_id", user_message.restaurant_id).execute()
        if not response:
            return "No promotions information is currently available."
        return response.data
    except Exception as e:
        return f"Error retrieving promotions: {str(e)}"


# ==========================================
# ORDER MANAGEMENT (USING CARTS & CART_ITEMS TABLES)
# ==========================================


# Carts
def get_carts(user_message: Message) -> list | str:
    """
    Returns historical list of carts for the user from the 'carts' table.
    """
    try:
        # Fetch open cart with its items
        carts = supabase.table("carts")\
            .select("id, status, cart_items(id, menu_items(id, name, description, price))")\
            .eq("wa_id", user_message.wa_id)\
            .eq("restaurant_id", user_message.restaurant_id)\
            .execute()

        print(f"Carts response: {carts}")

        if carts.data:
            return carts.data
            
        return "No active carts found."
    except Exception as e:
        print(f"Error fetching carts: {str(e)}")
        return f"Error fetching carts: {str(e)}"


def get_or_create_cart(user_message: Message) -> str:
    """
    Creates a new row in the 'carts' table.
    """
    try:
        existing_cart = supabase.table("carts")\
            .select("id")\
            .eq("conversation_id", user_message.conversation_id)\
            .eq("status", "open")\
            .limit(1).execute()
            
        if existing_cart.data:
             return f"You already have an open cart. Cart ID: {existing_cart.data}"

        new_cart = {
            "wa_id": user_message.wa_id,
            "restaurant_id": user_message.restaurant_id,
            "conversation_id": user_message.conversation_id,
            "status": "open",
        }
        
        new_cart = supabase.table("carts").insert(new_cart).execute()
        if new_cart.data:
            return f"New cart started. Cart ID: {new_cart.data}"
        return "Failed to create cart."
        
    except Exception as e:
        return f"Error creating cart: {str(e)}"


def update_cart(user_message: Message, cart_id: str, status: str) -> str:
    """
    Updates the 'status' column in the 'carts' table.
    """
    try:
        updated_cart = supabase.table("carts").update({"status": status}).eq("id", cart_id).execute()
        
        if updated_cart.data:
            return f"Cart {cart_id} status updated to {status}."
        return "Cart ID not found."
    except Exception as e:
        return f"Error updating cart: {str(e)}"


# Items
def checkout_cart(user_message: Message, cart_id: str) -> str:
    """
    Checks out the cart and creates an order.
    """
    try:
        cart_items = supabase.table("cart_items").select("id, menu_items(id, name, description, price)").eq("cart_id", cart_id).execute()

        total_price = 0
        if cart_items.data:
            for item in cart_items.data:
                total_price += item['menu_items']['price']

            return f"Generated a checkout order for the cart (https://app.recurrente.com/s/apitec/pay_exlqmqly). The user order is as follows: {cart_items.data}. The total price is: {total_price}."
        else:
            return "No items in the cart."
    except Exception as e:
        return f"Error checking out cart: {str(e)}"


def add_cart_items(user_message: Message, cart_id: str, menu_item_ids: list) -> str:
    """
    Adds rows to the 'cart_items' table.
    Expects 'items' to be a list of item names.
    """
    try:
        new_items = supabase.table("cart_items").insert([{"cart_id": cart_id, "menu_item_id": menu_item_id} for menu_item_id in menu_item_ids]).execute()
        if new_items.data:
            return f"Added the following items to the cart: {new_items.data}."
    except Exception as e:
        return f"Error adding items to the cart: {str(e)}"


def get_cart_items(user_message: Message, cart_id: str) -> list | str:
    """
    Retrieves rows from 'cart_items'.
    """
    try:
        cart_items = supabase.table("cart_items")\
            .select("id, menu_item(id, name, description, price)")\
            .eq("cart_id", cart_id)\
            .execute()
            
        if cart_items.data:
            return cart_items.data
        return "No items in this cart."
    except Exception as e:
        return f"Error getting items from cart: {str(e)}"


def remove_cart_items(user_message: Message, cart_id: str, cart_item_ids: list) -> str:
    """
    Deletes rows from 'cart_items'.
    """
    try:
        removed_items = supabase.table("cart_items").eq("cart_id", cart_id).delete().in_("id", cart_item_ids).execute()
        
        if removed_items.data:
            return f"Successfully removed the following items from the cart: {', '.join([item['menu_item']['name'] for item in removed_items.data])}."
        return "No items found to remove."
    except Exception as e:
        return f"Error removing items from cart: {str(e)}"


# ==========================================
# TOOL DEFINITIONS
# ==========================================


functions = {
    'get_bots': {
        'decalration': {
            'name': 'get_bots',
            'description': 'Use this to get a list of bots for the restaurant.',
        },
        'function': get_bots,
    },
    'transfer_conversation': {
        'decalration': {
            'name': 'transfer_conversation',
            'description': 'Use this to transfer the conversation to a different bot when the user requests to transfer the conversation to a different bot. To send the user back to the entry point router, do not provide a bot_id.',
        },
        'parameters': {
            'type': 'object',
            'properties': {
                'bot_id': {'type': 'string'},
            },
            'required': [],
        },
        'function': transfer_conversation,
    },
    'end_conversation': {
        'decalration': {
            'name': 'end_conversation',
            'description': 'Use this to end the conversation when the user requests to end the conversation or the conversation is no longer needed because the user has completed their request.',
        },
        'function': end_conversation,
    },
    'answer_faq': {
        'decalration': {
            'name': 'answer_faq',
            'description': 'Returns a list of FAQs with corresponding answers',
        },
        'function': answer_faq, # Assumed defined elsewhere
    },
    'get_menu': {
        'decalration': {
            'name': 'get_menu',
            'description': 'Use this to get a list of menu items when asked about the menu or when adding items to an order',
        },
        'function': get_menu, # Assumed defined elsewhere
    },
    'get_promotions': {
        'decalration': {
            'name': 'get_promotions',
            'description': 'Use this to get a list of promotions for the restaurant without waiting for a user to ask about promotions and apply them to the order.',
        },
        'function': get_promotions,
    },
    'get_or_create_cart': {
        'decalration': {
            'name': 'get_or_create_cart',
            'description': 'Use this to get the active cart for the user or create a new cart if a user does not have an open cart.',
        },
        'function': get_or_create_cart,
    },
    'get_carts': {
        'decalration': {
            'name': 'get_carts',
            'description': 'Use this to get a historical list of all carts for the user.',
        },
        'function': get_carts,
    },
    'update_cart': {
        'decalration': {
            'name': 'update_cart',
            'description': 'Use this to update an order status when the user requests to cancel or complete the order.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'cart_id': {'type': 'string'},
                    'status': {'type': 'string', 'enum': ['open', 'completed', 'abandoned', 'cancelled']},
                },
                'required': ['cart_id', 'status'],
            }
        },
        'function': update_cart,
    },
    'add_cart_items': {
        'decalration': {
            'name': 'add_cart_items',
            'description': 'Use this to add items to an open cart. MUST match menu item IDs exactly.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'cart_id': {'type': 'string'},
                    'menu_item_ids': {'type': 'array', 'items': {'type': 'string'}, 'description': 'List of exact menu item IDs from the menu'},
                },
                'required': ['cart_id', 'menu_item_ids'],
            }
        },
        'function': add_cart_items,
    },
    'get_cart_items': {
        'decalration': {
            'name': 'get_cart_items',
            'description': 'Use this to get detailed item list including IDs for removing items.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'cart_id': {'type': 'string'},
                },
                'required': ['cart_id'],
            }
        },
        'function': get_cart_items,
    },
    'remove_cart_items': {
        'decalration': {
            'name': 'remove_cart_items',
            'description': 'Use this if a user requests to remove items. Requires specific item IDs found via get_cart_items.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'cart_id': {'type': 'string'},
                    'cart_item_ids': {'type': 'array', 'items': {'type': 'string'}},
                },
                'required': ['cart_item_ids'],
            }
        },
        'function': remove_cart_items,
    },
    'checkout_cart': {
        'decalration': {
            'name': 'checkout_cart',
            'description': 'Use this when the user is ready to checkout the cart and pay for the items. This will calculate the total price of the cart and generate a payment link.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'cart_id': {'type': 'string'},
                },
                'required': ['cart_id'],
            }
        },
        'function': checkout_cart,
    },
};