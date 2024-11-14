from pyrogram import Client, filters
from pyrogram.types import Message
import asyncio
from aiohttp import web

# Initialize the bot with your credentials
app = Client(
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

@app.on_message(filters.command("start") & filters.private)
async def start_command(client, message: Message):
    user_id = message.from_user.id
    
    # Generate a unique link for the user if not already generated
    if user_id not in user_links:
        user_links[user_id] = f"https://t.me/KantaBaiBot?start={user_id}"
    
    # Send the group link to the user
    await message.reply(f"Please join our group to proceed: https://t.me/{group_id}")
    await message.reply("After joining, type /verify to receive the original link.")

@app.on_message(filters.command("verify") & filters.private)
async def verify_command(client, message: Message):
    user_id = message.from_user.id
    
    # Check if the user has joined the group
    try:
        member = await app.get_chat_member(group_id, user_id)
        if member.status in ["member", "administrator", "creator"]:
            # User is a member, send the original link
            await message.reply(f"Thank you for joining! Here’s your original link: {original_link}")
        else:
            await message.reply("You need to join the group to receive the link.")
    except Exception as e:
        await message.reply("It seems you haven't joined the group yet. Please join and try again.")
        print(f"Error: {e}")

# Health check endpoint
async def health_check(request):
    return web.Response(text="Bot is running")

# Setup HTTP server for health checks
async def start_health_server():
    server = web.Application()
    server.router.add_get("/health", health_check)
    runner = web.AppRunner(server)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()
    print("Health check server running on http://0.0.0.0:8080/health")

# Start both bot and health server
async def main():
    await asyncio.gather(
        app.start(),
        start_health_server()
    )

asyncio.run(main())
