import os
import discord
from google import genai

# Environment variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

OWNER_ID = 1365256422585274398
ALLOWED_CHANNEL_ID = None

# Gemini
client = genai.Client(api_key=GEMINI_API_KEY)

# Discord
intents = discord.Intents.default()
intents.message_content = True

bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_message(message):
    global ALLOWED_CHANNEL_ID

    print(f"Message received: {message.content}")

    # Ignore bots
    if message.author.bot:
        return

    # Owner-only commands
    if message.content == "!setchannel" and message.author.id == OWNER_ID:
        ALLOWED_CHANNEL_ID = message.channel.id
        await message.channel.send(
            f"✅ AI channel set to <#{ALLOWED_CHANNEL_ID}>"
        )
        return

    if message.content == "!removechannel" and message.author.id == OWNER_ID:
        ALLOWED_CHANNEL_ID = None
        await message.channel.send(
            "✅ Channel restriction removed."
        )
        return

    # Channel restriction
    if (
        ALLOWED_CHANNEL_ID is not None
        and message.channel.id != ALLOWED_CHANNEL_ID
    ):
        return

    # Use every message as prompt
    prompt = message.content.strip()

    if not prompt:
        return

    try:
        print("Reached Gemini")

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"""
You are a Discord AI bot.

Your creator is Akhilesh.

If someone asks who created you, answer:
"My creator is Akhilesh."

If you are talking to user ID 1365256422585274398,
call them "Owner".

User message:
{prompt}
"""
        )

        reply = response.text or "No response generated."

        await message.channel.send(reply[:2000])

    except Exception as e:
        error_text = str(e)

        if "429" in error_text:
            await message.channel.send(
                "⏳ Rate limit reached. Please wait a minute and try again."
            )
        elif "503" in error_text:
            await message.channel.send(
                "⚠️ Gemini is currently overloaded. Try again later."
            )
        else:
            await message.channel.send(
                f"❌ Error: {error_text}"
            )

bot.run(DISCORD_TOKEN)
