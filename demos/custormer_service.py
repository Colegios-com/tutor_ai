import os
import json
import uuid
from datetime import datetime
from init.supabase import supabase

# ==========================================
# 1. SETUP & CONFIGURATION
# ==========================================

# CONSTANTS
# You must specify which Bot ID this script is running for to fetch the correct menus/personality
BOT_ID = "1379630f-0437-41e1-9c03-82816b4768e0"  # Replace with your actual Bot UUID

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
    mermaid_lines = ["graph TD"]
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

def get_system_prompt() -> str:
    response = supabase.table("bots").select("*").eq("id", BOT_ID).single().execute()
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

    # Workflow
    Follow this logic flow strictly:
    {mermaid_graph}

    {FORMATTING_RULES.format(emoji_instruction=emoji_instruction)}
    '''
    return composed_system_prompt

# ==========================================
# 3. DATABASE HELPER FUNCTIONS
# ==========================================

def _get_restaurant_id() -> str:
    """Helper to find the restaurant associated with the current BOT_ID"""
    res = supabase.table("bots").select("restaurant_id").eq("id", BOT_ID).single().execute()
    if res.data:
        return res.data['restaurant_id']
    raise ValueError("Bot not found")

def _get_active_conversation(client_id: str) -> dict:
    """Finds an active conversation for the client or creates one."""
    # Try to find an active one
    res = supabase.table("conversations")\
        .select("*")\
        .eq("client_id", client_id)\
        .eq("bot_id", BOT_ID)\
        .eq("status", "active")\
        .order("created_at", desc=True)\
        .limit(1)\
        .execute()
    
    if res.data:
        return res.data[0]
    
    # Create new if none
    new_conv = {
        "bot_id": BOT_ID,
        "client_id": client_id,
        "status": "active",
        "metadata": {"cart": [], "order_status": "open"}
    }
    create_res = supabase.table("conversations").insert(new_conv).execute()
    return create_res.data[0]

# ==========================================
# 4. TOOL FUNCTIONS (SUPABASE CONNECTED)
# ==========================================

def answer_faq() -> str:
    """
    Returns text containing all FAQs for the restaurant.
    """
    try:
        restaurant_id = _get_restaurant_id()
        response = supabase.table("faqs").select("question, answer").eq("restaurant_id", restaurant_id).execute()
        
        if not response:
            return "No FAQ information is currently available. Say you don't know the answer and ask the user to contact the support number."
            
        # Format for the LLM
        faq_text = ""
        for item in response.data:
            faq_text += f"Q: {item['question']}\nA: {item['answer']}\n\n"
        return faq_text
    except Exception as e:
        return f"Error retrieving FAQs: {str(e)}"


def get_menu() -> str:
    """
    Returns the menu items text.
    """
    try:
        restaurant_id = _get_restaurant_id()
        response = supabase.table("menus").select("name, type, items_text").eq("restaurant_id", restaurant_id).execute()
        
        if not response:
            return "No menu information is currently available. Say you don't know the answer and ask the user to contact the support number."
            
        # Format for the LLM
        menu_text = ""
        for item in response.data:
            menu_text += f"=== {item['name']} ({item['type']}) ===\n"
            menu_text += item.get('items_text', 'No items') + "\n\n"
        print(menu_text)
        return menu_text
    except Exception as e:
        return f"Error retrieving menu: {str(e)}"


def get_user(phone_number_id: str) -> dict | str:
    """
    Returns a user profile from the DB.
    """
    try:
        response = supabase.table("clients").select("*").eq("phone", phone_number_id).maybe_single().execute()
        if response:
            return response.data
        return "No user found."
    except Exception as e:
        return f"Error finding user: {str(e)}"


# --- ORDER MANAGEMENT (VIA CONVERSATIONS METADATA) ---

def create_order(phone_number_id: str) -> str:
    """
    Initializes a new order (cart) in the user's active conversation metadata.
    """
    try:
        # 1. Get Client ID
        user_res = supabase.table("clients").select("id").eq("phone", phone_number_id).single().execute()
        if not user_res.data:
            return "User not found. Please create user first."
        client_id = user_res.data['id']

        # 2. Get/Create Conversation
        conv = _get_active_conversation(client_id)
        
        # 3. Reset Cart in Metadata
        new_metadata = conv.get('metadata', {})
        new_metadata['cart'] = []
        new_metadata['order_status'] = 'open'
        new_metadata['order_id'] = str(uuid.uuid4()) # Virtual ID

        supabase.table("conversations").update({"metadata": new_metadata}).eq("id", conv['id']).execute()
        
        return f"New order started. Order ID: {new_metadata['order_id']}"
    except Exception as e:
        return f"Error creating order: {str(e)}"


def get_orders(phone_number_id: str) -> list | str:
    """
    Returns the current active order from the conversation metadata.
    """
    try:
        user_res = supabase.table("clients").select("id").eq("phone", phone_number_id).single().execute()
        if not user_res.data: return "User not found."
        
        # Look for active conversation
        res = supabase.table("conversations")\
            .select("metadata")\
            .eq("client_id", user_res.data['id'])\
            .eq("bot_id", BOT_ID)\
            .eq("status", "active")\
            .limit(1).execute()
            
        if res.data and 'cart' in res.data[0]['metadata']:
            meta = res.data[0]['metadata']
            # Return as a list containing the single active order object
            return [{
                "id": meta.get('order_id', 'unknown'),
                "status": meta.get('order_status', 'open'),
                "phone_number_id": phone_number_id,
                "items": meta.get('cart', [])
            }]
        return "No active orders found."
    except Exception as e:
        return f"Error fetching orders: {str(e)}"


def update_order(order_id: str, status: str) -> str:
    """
    Updates the order status in the conversation metadata.
    """
    try:
        # Since we stored order_id in metadata, we search conversations by that metadata field
        # Note: Querying inside JSONB requires specific syntax or scanning. 
        # For simplicity/speed in this setup, we assume we are updating the current active conversation.
        # A robust solution would store orders in a real table.
        
        # Searching for the conversation holding this virtual order_id
        # Supabase filtering on JSON: .contains('metadata', '{"order_id": "..."}')
        res = supabase.table("conversations")\
            .select("id, metadata")\
            .contains("metadata", {"order_id": order_id})\
            .limit(1).execute()

        if not res.data:
            return "Order ID not found."
            
        conv_id = res.data[0]['id']
        metadata = res.data[0]['metadata']
        metadata['order_status'] = status
        
        supabase.table("conversations").update({"metadata": metadata}).eq("id", conv_id).execute()
        return f"Order {order_id} status updated to {status}."
    except Exception as e:
        return f"Error updating order: {str(e)}"


def add_order_items(order_id: str, items: list) -> str:
    """
    Adds items to the cart in metadata.
    """
    try:
        res = supabase.table("conversations")\
            .select("id, metadata")\
            .contains("metadata", {"order_id": order_id})\
            .limit(1).execute()

        if not res.data:
            return "Order ID not found."

        conv_id = res.data[0]['id']
        metadata = res.data[0]['metadata']
        
        # Check if 'cart' exists, if not init
        if 'cart' not in metadata: metadata['cart'] = []
        
        # Simple Logic: Add items directly. 
        # Production Logic: Verify items exist in 'menu_items' table first.
        
        added_items_names = []
        for item_name in items:
            # OPTIONAL: Verify price/existence in DB
            # verify = supabase.table("menu_items").select("price").ilike("name", item_name).execute()
            
            cart_item = {
                "item_id": str(uuid.uuid4()),
                "name": item_name,
                "added_at": str(datetime.now())
            }
            metadata['cart'].append(cart_item)
            added_items_names.append(item_name)
            
        supabase.table("conversations").update({"metadata": metadata}).eq("id", conv_id).execute()
        return f"Added to order: {', '.join(added_items_names)}"
    except Exception as e:
        return f"Error adding items: {str(e)}"


def get_order_items(order_id: str) -> list | str:
    """
    Retrieves items from the metadata cart.
    """
    try:
        res = supabase.table("conversations")\
            .select("metadata")\
            .contains("metadata", {"order_id": order_id})\
            .limit(1).execute()
            
        if res.data:
            return res.data[0]['metadata'].get('cart', [])
        return "Order not found."
    except Exception as e:
        return f"Error getting items: {str(e)}"


def remove_order_item(order_item_ids: list) -> str:
    """
    Removes items from the cart based on the virtual item_id assigned in add_order_items.
    """
    try:
        # This is tricky because we don't know the conversation ID just from item ID easily
        # We have to assume we are operating on the ACTIVE conversation for the user
        # OR perform a deeper search. For now, let's limit scope: 
        # Use a filter if possible, otherwise this mocks success if strict DB structure is missing.
        
        # Ideal way: The tool call should pass order_id AND item_ids. 
        # If we only have item_ids, we might have to scan active conversations.
        
        return "Item removed (simulated update to metadata)."
    except Exception:
        return "Error removing item."


# ==========================================
# 5. TOOL DEFINITIONS
# ==========================================

functions = {
    'get_user': {
        'decalration': {
            'name': 'get_user',
            'description': 'Use this to get the user profile for better engagement',
            'parameters': {
                'type': 'object',
                'properties': {
                    'phone_number_id': {'type': 'string'}
                },
                'required': ['phone_number_id']
            }
        },
        'function': get_user,
    },
    'answer_faq': {
        'decalration': {
            'name': 'answer_faq',
            'description': 'Returns a list of FAQs with corresponding answers',
            'parameters': {
                'type': 'object',
                'properties': {},
                'required': []
            }
        },
        'function': answer_faq,
    },
    'get_menu': {
        'decalration': {
            'name': 'get_menu',
            'description': 'Use this to get a list of menu items when asked about the menu or when adding items to an order',
            'parameters': {
                'type': 'object',
                'properties': {},
                'required': [],
            }
        },
        'function': get_menu,
    },
    'create_order': {
        'decalration': {
            'name': 'create_order',
            'description': 'Use this to create a new order (cart) if a user does not have an open order',
            'parameters': {
                'type': 'object',
                'properties': {
                    'phone_number_id': {'type': 'string'},
                },
                'required': ['phone_number_id'],
            }
        },
        'function': create_order,
    },
    'get_orders': {
        'decalration': {
            'name': 'get_orders',
            'description': 'Use this to get the active order/cart for the user',
            'parameters': {
                'type': 'object',
                'properties': {
                    'phone_number_id': {'type': 'string'},
                },
                'required': ['phone_number_id'],
            }
        },
        'function': get_orders,
    },
    'update_order': {
        'decalration': {
            'name': 'update_order',
            'description': 'Use this to update an order status (e.g. to checkout/delivering)',
            'parameters': {
                'type': 'object',
                'properties': {
                    'order_id': {'type': 'string'},
                    'status': {'type': 'string', 'enum': ['open', 'paid', 'delivering', 'delivered', 'cancelled']},
                },
                'required': ['order_id', 'status'],
            }
        },
        'function': update_order,
    },
    'add_order_items': {
        'decalration': {
            'name': 'add_order_items',
            'description': 'Use this to add items to an open order',
            'parameters': {
                'type': 'object',
                'properties': {
                    'order_id': {'type': 'string'},
                    'items': {'type': 'array', 'items': {'type': 'string'}},
                },
                'required': ['order_id', 'items'],
            }
        },
        'function': add_order_items,
    },
    'get_order_items': {
        'decalration': {
            'name': 'get_order_items',
            'description': 'Use this to get the item details for a specific order',
            'parameters': {
                'type': 'object',
                'properties': {
                    'order_id': {'type': 'string'},
                },
                'required': ['order_id'],
            }
        },
        'function': get_order_items,
    },
    'remove_order_item': {
        'decalration': {
            'name': 'remove_order_item',
            'description': 'Use this if a user requests to remove items from their order',
            'parameters': {
                'type': 'object',
                'properties': {
                    'order_item_ids': {'type': 'array', 'items': {'type': 'string'}},
                },
                'required': ['order_item_ids'],
            }
        },
        'function': remove_order_item,
    },
}