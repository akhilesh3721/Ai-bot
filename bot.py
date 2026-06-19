import os
import discord
from discord.ext import commands
from openai import OpenAI

# =========================
# CONFIG
# =========================

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

OWNER_ID = 1365256422585274398

ALLOWED_CHANNEL_ID = None
memory = {}

# =========================
# OPENROUTER
# =========================

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

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
📖 Mini Luffy Commands

!ping
!help
!clearmemory

Owner:
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

    await ctx.send("🧠 Memory cleared.")

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

    memory[user_id] = memory[user_id][-8:]

    messages = [
        {
            "role": "system",
            "content": f"""
You are Mini Luffy.

Your creator is Akhilesh.

If anyone asks who created you:
"My creator is Akhilesh."

Current user:
Username: {message.author.name}
User ID: {message.author.id}

Only call user ID {OWNER_ID} Owner.

Never confuse users.

Personality:
- Friendly
- Talkative
- Helpful
- Funny
- Slightly sarcastic
- Uses emojis naturally

Keep replies under 1500 characters.
"""
        }
    ]

    messages.extend(memory[user_id])

    try:
        async with message.channel.typing():

            chat = client.chat.completions.create(
                model="deepseek/deepseek-chat",
                messages=messages,
                temperature=0.8,
                max_tokens=1000
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

        memory[user_id] = memory[user_id][-8:]

        await message.channel.send(
            reply[:2000]
        )

    except Exception as e:
        error_text = str(e)

        print(error_text)

        if "rate_limit" in error_text.lower():
            await message.channel.send(
                "⏳ API rate limit reached. Try again later."
            )
        else:
            await message.channel.send(
                "❌ Something went wrong."
            )

# =========================
# START BOT
# =========================

bot.run(DISCORD_TOKEN)
