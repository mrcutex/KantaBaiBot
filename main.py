from pyrogram import Client, filters, enums, idle
from pyrogram.types import Message
from pyrogram.errors import FloodWait, UserNotParticipant
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
    await message.reply(f"Please join our group to proceed: https://t.me/+_965RzDS4BUwZGU1")
    await message.reply("After joining, type /verify to receive the original link.")

@bot.on_message(filters.command("verify") & filters.private)
async def verify_command(client, message: Message):
    user_id = message.from_user.id
    
    try:
        # Fetch the member's status in the group
        member_info = await client.get_chat_member(group_id, user_id)
        status = member_info.status
        
        # Determine the user's status
        if status == enums.ChatMemberStatus.OWNER:
            user_status = "Owner"
        elif status == enums.ChatMemberStatus.ADMINISTRATOR:
            user_status = "Admin"
        elif status == enums.ChatMemberStatus.MEMBER:
            user_status = "Member"
        elif status == enums.ChatMemberStatus.RESTRICTED:
            user_status = "Restricted"
        elif status == enums.ChatMemberStatus.LEFT:
            user_status = "Left"
        elif status == enums.ChatMemberStatus.BANNED:
            user_status = "Banned"
        
        # If user is a member, send the original link
        if user_status in ["Admin", "Member"]:
            await message.reply(f"Thank you for joining! Here’s your original link: {original_link}")
        else:
            await message.reply(f"You are {user_status}. You need to join the group to receive the link.")
        
    except UserNotParticipant:
        # Handle the case where the user is not in the group
        await message.reply("You are not in the group. Please join the group to get the link.")
    
    except FloodWait as e:
        # Handle flood wait by pausing the execution
        logger.warning(f"Flood wait: Sleeping for {e.x} seconds.")
        await asyncio.sleep(e.x)
        await verify_command(client, message)
    
    except Exception as e:
        # Log any other exceptions and notify the user
        logger.error(f"Error in verification: {e}")
        await message.reply("It seems something went wrong. Please try again later.")

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
