import os
import discord
from google import genai

# Load tokens from environment variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OWNER_ID = 1365256422585274398
ALLOWED_CHANNEL_ID = None
# Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)

# Discord setup
intents = discord.Intents.default()
intents.message_content = True

bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    global ALLOWED_CHANNEL_ID
    if message.content == "!setchannel" and message.author.id == OWNER_ID:
        ALLOWED_CHANNEL_ID = message.channel.id
        await message.channel.send(
            f"✅ AI channel set to <#{ALLOWED_CHANNEL_ID}>"
        )
        return
    if message.content == "!removechannel" and message.author.id == OWNER_ID:
        ALLOWED_CHANNEL_ID = None
        await message.channel.send("✅ Channel restriction removed.")
        return
    if ALLOWED_CHANNEL_ID is not None and message.channel.id != ALLOWED_CHANNEL_ID:
        return
    if message.content.startswith("!ai"):
        prompt = message.content[4:].strip()

        if not prompt:
            await message.channel.send("Please provide a prompt.")
            return

        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"""
            Your creator is Akhilesh.
            If anyone asks who created you, answer: "My creator is Akhilesh."
            If you are talking to user ID 1365256422585274398, call them "Owner".
            User message: {prompt}
            """
            )

            await message.channel.send(response.text[:2000])

        except Exception as e:
    if "429" in str(e):
        await message.channel.send(
            "⏳ Rate limit reached. Please wait a minute and try again."
        )
    elif "503" in str(e):
        await message.channel.send(
            "⚠️ Gemini is currently overloaded. Try again later."
        )
    else:
        await message.channel.send(f"Error: {e}")

bot.run(DISCORD_TOKEN)
