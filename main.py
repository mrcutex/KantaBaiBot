from pyrogram import Client, filters, enums, idle
from pyrogram.types import Message
from pyrogram.errors import FloodWait, UserNotParticipant, PeerIdInvalid
import asyncio
import threading
import logging
from flask import Flask
import random

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

# Dictionary to store original links, unique start links, and user mappings
original_links = []  # List to hold all original links
link_mapping = {}     # Mapping of start links to original links
user_links = {}       # Mapping of users to their unique links

# Group ID and group join link
OWNER_USER_ID = 7305252437  # Replace with your actual user ID
group_id = "-1002252756157"
group_join_link = "https://t.me/+_965RzDS4BUwZGU1"  # Group join link

# Generate a unique start link for each original link
def generate_start_link(user_id, link_index):
    return f"https://t.me/KantaBaiBot?start={user_id}_{link_index}"

@bot.on_message(filters.command("start") & filters.private)
async def start_command(client, message: Message):
    user_id = message.from_user.id
    start_link = message.text.split("start=")[1]  # Extract the unique start link parameter
    
    # If the user started with a valid unique link, map them to the original link
    if start_link in link_mapping:
        await message.reply(f"Please join our group to proceed: {group_join_link}")
        await message.reply("After joining, type /verify to receive the original link.")
    else:
        await message.reply("Invalid start link. Please make sure you're using a valid link.")

@bot.on_message(filters.command("verify") & filters.private)
async def verify_command(client, message: Message):
    user_id = message.from_user.id

    # Check if the user has joined the group
    try:
        member_info = await client.get_chat_member(group_id, user_id)

        # If the user is a member, provide a link from the mapping
        if member_info.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.MEMBER]:
            if user_id in user_links:
                # Get the original link based on the user's start link
                original_link = original_links[user_links[user_id]]
                await message.reply(f"Thank you for joining! Here’s your original link: {original_link}")
            else:
                await message.reply("You need to start the bot with a valid unique link.")
        else:
            await message.reply(f"You need to join the group to receive the link. Please join here: {group_join_link}")
    except UserNotParticipant:
        await message.reply(f"You need to join the group to receive the link. Please join here: {group_join_link}")
    except PeerIdInvalid:
        await message.reply("It seems you haven't interacted with the group yet. Please join and then try again.")
    except FloodWait as e:
        logger.warning(f"Flood wait: Sleeping for {e.x} seconds.")
        await asyncio.sleep(e.x)
        await verify_command(client, message)
    except Exception as e:
        logger.error(f"Error in verification: {e}")
        await message.reply("It seems something went wrong. Please try again later.")

# List of random texts you can use (you can customize this list)
random_texts = [
    "CoolUser123", "LuckyPlayer", "HappyExplorer", "MightyWarrior", "SpeedyGamer",
    "DreamChaser", "TechGuru", "BoldAdventurer", "SilentHunter", "WildCard"
]

# Dictionary to store used random texts for each link
used_random_texts = {}

@bot.on_message(filters.command("addlink") & filters.private)
async def add_link(client, message: Message):
    # Only allow the owner to add new links
    if message.from_user.id != OWNER_USER_ID:
        await message.reply("You are not authorized to add new links.")
        return

    # Add the new link to the original links list
    new_link = message.text.split(" ", 1)[1]  # Get the link after the command
    original_links.append(new_link)

    # Initialize used random texts list for this link if not already initialized
    link_index = len(original_links) - 1  # Get the index of the new link
    if link_index not in used_random_texts:
        used_random_texts[link_index] = set()  # Set to keep track of used random texts for this link

    # Generate unique start link for this new original link
    available_random_texts = list(set(random_texts) - used_random_texts[link_index])
    if available_random_texts:
        random_text = random.choice(available_random_texts)  # Select a random text from the available ones
        new_start_link = f"https://t.me/KantaBaiBot?start={random_text}_{link_index}"  # Unique start link
        link_mapping[new_start_link] = new_link

        # Mark this random text as used for this link
        used_random_texts[link_index].add(random_text)
        
        # Send the new start link to the owner
        await message.reply(f"New original link added: {new_link}")
        await message.reply(f"Generated unique start link for the new original link:\n{new_start_link}")
    else:
        await message.reply(f"No more unique random texts available for this link.")

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
