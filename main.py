# Init
from init.fast_api import app
from init.whatsapp import whatsapp_client

# Storage
from storage.storage import add_messages

# Utilities
from utilities.message_parser import verify_message_payload, is_duplicate_message, build_user_message
from utilities.response_orchestrator import orchestrate_response

# Async
import asyncio
from fastapi import Request, Query, BackgroundTasks


@app.get('/whatsapp/')
async def whatsapp_webhook(hub_mode: str = Query(..., alias='hub.mode'), hub_challenge: int = Query(..., alias='hub.challenge'), hub_verify_token: str = Query(..., alias='hub.verify_token')):
    if hub_mode == 'subscribe' and hub_verify_token == '!MdA3tCPvdyIdPg&':
        return hub_challenge
    else:
        return 'Invalid request.'


@app.post('/whatsapp/', status_code=200)
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    payload = await request.json()


    if not verify_message_payload(payload):
        return True
    
    if is_duplicate_message(payload):
        return True
    
    user_message = build_user_message(payload)

    add_messages(user_messages=[user_message])

    # --- 1. Define the Keep-Alive Function ---
    async def keep_typing_alive():
        try:
            count = 1
            while True:
                # Send the indicator
                # Note: If whatsapp_client methods are synchronous, wrap them if needed, 
                # but standard HTTP requests are fast enough to just call here.
                whatsapp_client.send_typing_indicator(user_message=user_message)
                count += 1
                # Wait 20 seconds (WhatsApp indicators expire after ~25s, so 20s is safe)
                await asyncio.sleep(20)
        except asyncio.CancelledError:
            # This allows the task to stop cleanly when we cancel it
            pass

    # --- 2. Start the Task ---
    typing_task = asyncio.create_task(keep_typing_alive())

    try:
        # --- 3. Run your main logic ---
        # IMPORTANT: orchestrate_response needs to be compatible with async execution.
        
        # OPTION A: If orchestrate_response is already 'async def':
        # response_message = await orchestrate_response(user_message=user_message)
        
        # OPTION B: If orchestrate_response is synchronous (blocking), run it in a thread
        # This is required so the typing loop doesn't get frozen.
        response_message = await asyncio.to_thread(orchestrate_response, user_message=user_message)

    finally:
        # --- 4. Stop the typing loop ---
        # This block runs whether the response succeeded or failed
        typing_task.cancel()

    if not response_message:
        return False

    # Save messages (If add_messages is DB heavy, consider awaiting it or offloading it)
    add_messages(user_messages=[response_message])

    return True
