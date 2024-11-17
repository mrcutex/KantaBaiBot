from pyrogram import Client, filters, idle
from pyrogram.types import Message
from pyrogram.errors import FloodWait
import asyncio
import threading
import logging
from flask import Flask

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Flask app for health check
flask_app = Flask(__name__)

@flask_app.route('/health')
def health():
    return 'OK', 200

def run_server():
    flask_app.run(host='0.0.0.0', port=8000)

# Start Flask server in a separate thread
threading.Thread(target=run_server, daemon=True).start()

# Initialize the bot with your credentials
bot = Client(
    "unique_link_bot",
    api_id="10276529",
    api_hash="693b95dbf7fa563ee5bf1e9cb8f937f1",
    bot_token="7409932510:AAFQ5ETpB4XQK3QH989zCvj5rmDLTLJeaZQ"
)

# Dictionary to store unique links and their respective users
user_links = {}

# Group ID and original link
group_id = "-1002252756157"
original_link = "https://example.com/original"

@bot.on_message(filters.command("start") & filters.private)
async def start_command(client, message: Message):
    user_id = message.from_user.id
    
    # Generate a unique link for the user if not already generated
    if user_id not in user_links:
        user_links[user_id] = f"https://t.me/KantaBaiBot?start={user_id}"
    
    # Send the group link to the user
    await message.reply(f"Please join our group to proceed: https://t.me/{group_id}")
    await message.reply("After joining, type /verify to receive the original link.")

@bot.on_message(filters.command("verify") & filters.private)
async def verify_command(client, message: Message):
    user_id = message.from_user.id
    
    # Check if the user has joined the group
    try:
        member = await bot.get_chat_member(group_id, user_id)
        if member.status in ["member", "administrator", "creator"]:
            # User is a member, send the original link
            await message.reply(f"Thank you for joining! Here’s your original link: {original_link}")
        else:
            await message.reply("You need to join the group to receive the link.")
    except FloodWait as e:
        # Handle flood wait by pausing the execution
        logger.warning(f"Flood wait: Sleeping for {e.x} seconds.")
        await asyncio.sleep(e.x)
        # Retry after the sleep
        await verify_command(client, message)
    except Exception as e:
        logger.error(f"Error in verification: {e}")
        await message.reply("It seems you haven't joined the group yet. Please join and try again.")

# Main entry point to run bot and health check server concurrently
async def main():
    try:
        await bot.start()
        logger.info("Bot started...")        
        await idle()
    except KeyboardInterrupt:
        await bot.stop()
        logger.info("Bot stopped")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
