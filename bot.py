import os
import json
import discord
from discord.ext import commands
from groq import Groq

# =========================
# CONFIG
# =========================

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

OWNER_ID = 1365256422585274398
MEMORY_FILE = "memory.json"

ALLOWED_CHANNEL_ID = None

# =========================
# GROQ
# =========================

client = Groq(api_key=GROQ_API_KEY)

# =========================
# MEMORY
# =========================

def load_memory():
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_memory():
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2)

memory = load_memory()

# =========================
# DISCORD
# =========================

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)

# =========================
# EVENTS
# =========================

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

# =========================
# COMMANDS
# =========================

@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong!")

@bot.command()
async def help(ctx):
    await ctx.send(
        """
📖 Commands

!ping
!help
!clearmemory

Owner Only:
!setchannel
!removechannel

Mention me or reply to me to chat.
"""
    )

@bot.command()
async def clearmemory(ctx):
    user_id = str(ctx.author.id)

    if user_id in memory:
        del memory[user_id]
        save_memory()

    await ctx.send("🧠 Your memory has been cleared.")

@bot.command()
async def setchannel(ctx):
    global ALLOWED_CHANNEL_ID

    if ctx.author.id != OWNER_ID:
        return

    ALLOWED_CHANNEL_ID = ctx.channel.id

    await ctx.send(
        f"✅ AI channel set to <#{ALLOWED_CHANNEL_ID}>"
    )

@bot.command()
async def removechannel(ctx):
    global ALLOWED_CHANNEL_ID

    if ctx.author.id != OWNER_ID:
        return

    ALLOWED_CHANNEL_ID = None

    await ctx.send(
        "✅ Channel restriction removed."
    )

# =========================
# AI CHAT
# =========================

@bot.event
async def on_message(message):
    global ALLOWED_CHANNEL_ID

    if message.author.bot:
        return

    await bot.process_commands(message)

    # Channel lock
    if (
        ALLOWED_CHANNEL_ID is not None
        and message.channel.id != ALLOWED_CHANNEL_ID
    ):
        return

    should_reply = False

    # Mention bot
    if bot.user in message.mentions:
        should_reply = True

    # Reply to bot
    if message.reference:
        try:
            replied_message = await message.channel.fetch_message(
                message.reference.message_id
            )

            if replied_message.author.id == bot.user.id:
                should_reply = True

        except:
            pass

    if not should_reply:
        return

    prompt = message.content

    # Remove mention text
    prompt = prompt.replace(
        f"<@{bot.user.id}>",
        ""
    )

    prompt = prompt.replace(
        f"<@!{bot.user.id}>",
        ""
    )

    prompt = prompt.strip()

    if prompt == "":
        prompt = "Hello"

    user_id = str(message.author.id)

    if user_id not in memory:
        memory[user_id] = []

    memory[user_id].append(
        {
            "role": "user",
            "content": prompt
        }
    )

    memory[user_id] = memory[user_id][-20:]

    messages = [
        {
            "role": "system",
            "content": f"""
You are Mini Luffy.

Your creator is Akhilesh.

If anyone asks who created you:
"My creator is Akhilesh."

If talking to user ID {OWNER_ID},
call them Owner.

Personality:
- Friendly
- Talkative
- Helpful
- Slightly sarcastic
- Funny
- Uses emojis occasionally
- Remembers previous messages
- Explains things clearly

Keep replies under 1500 characters.
"""
        }
    ]

    messages.extend(memory[user_id])

    try:
        async with message.channel.typing():

            chat = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.8
            )

            reply = chat.choices[0].message.content

        if not reply:
            reply = "I couldn't think of a response."

        memory[user_id].append(
            {
                "role": "assistant",
                "content": reply
            }
        )

        memory[user_id] = memory[user_id][-20:]

        save_memory()

        await message.channel.send(
            reply[:2000]
        )

    except Exception as e:
        print(f"ERROR: {e}")

        await message.channel.send(
            f"❌ Error: {str(e)[:1800]}"
        )

# =========================
# START BOT
# =========================

bot.run(DISCORD_TOKEN)
