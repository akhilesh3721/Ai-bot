import os
import discord
from groq import Groq

# Environment variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

OWNER_ID = 1365256422585274398
ALLOWED_CHANNEL_ID = None

# Groq client
client = Groq(api_key=GROQ_API_KEY)

# Discord intents
intents = discord.Intents.default()
intents.message_content = True

bot = discord.Client(intents=intents)


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")


@bot.event
async def on_message(message):
    global ALLOWED_CHANNEL_ID

    print(f"📩 Message received: {message.content}")

    # Ignore bots
    if message.author.bot:
        return

    # Owner command: set channel
    if (
        message.content.lower() == "!setchannel"
        and message.author.id == OWNER_ID
    ):
        ALLOWED_CHANNEL_ID = message.channel.id

        await message.channel.send(
            f"✅ AI channel set to <#{ALLOWED_CHANNEL_ID}>"
        )
        return

    # Owner command: remove channel restriction
    if (
        message.content.lower() == "!removechannel"
        and message.author.id == OWNER_ID
    ):
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

    prompt = message.content.strip()

    if not prompt:
        return

    try:
        print("🚀 Sending request to Groq")

        chat = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": f"""
You are a Discord AI bot.

Your creator is Akhilesh.

If someone asks who created you, answer:
"My creator is Akhilesh."

If talking to user ID {OWNER_ID},
call them "Owner".

Be friendly and helpful.
"""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        reply = chat.choices[0].message.content

        if not reply:
            reply = "No response generated."

        await message.channel.send(reply[:2000])

    except Exception as e:
        print(f"ERROR: {e}")

        await message.channel.send(
            f"❌ Error: {str(e)[:1800]}"
        )


bot.run(DISCORD_TOKEN)
