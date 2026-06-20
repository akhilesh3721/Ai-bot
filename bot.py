import os
import discord
from discord.ext import commands
from openai import OpenAI
import base64
import requests
# =========================
# CONFIG
# =========================

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

OWNER_ID = 1365256422585274398

ALLOWED_CHANNEL_ID = None


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
#from memory import save_memory, get_memory

@bot.command()
async def remember(ctx, *, text):
    save_memory(
        ctx.author.id,
        ctx.author.name,
        text
    )
    await ctx.send("Saved!")
# =========================
# AI CHAT
# =========================

@bot.event
async def on_message(message):
    global ALLOWED_CHANNEL_ID
    mentioned_users = []
    for user in message.mentions:
        if user.id != bot.user.id:
            mentioned_users.append(
                f"{user.display_name} ({user.id})"
            )
    mentioned_text = "\n".join(mentioned_users)
    if not mentioned_text:
        mentioned_text = "None"

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
    # IMAGE ANALYSIS
    if message.attachments:
        image_url = message.attachments[0].url

        try:
            async with message.channel.typing():

                response = client.chat.completions.create(
                    model="google/gemma-3-27b-it",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": """
Analyze this image.

If it contains:
- People: describe appearance and actions.
- Animals: identify them.
- Minecraft: identify blocks, mobs and structures.
- Screenshots: explain what is shown.
- Text: read and summarize it.

Keep the response concise.
"""
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": image_url
                                    }
                                }
                            ]
                        }
                    ],
                    max_tokens=500
                )

            result = response.choices[0].message.content

            await message.reply(
                result[:2000],
                mention_author=False
            )

            return

        except Exception as e:
            print(f"Vision Error: {e}")

# 

    

    prompt = message.content
    username = message.author.name
    display_name = message.author.display_name
    user_id_num = message.author.id

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
    #save_memory(
    #message.author.id,
    #message.author.name,
    #prompt
    #)

    

    messages = [
        {
            "role": "system",
            "content": f"""
You are Mini Luffy.

Creator: Akhilesh.

Only call user ID 1365256422585274398 "Owner".

Personality:
- Friendly
- Helpful
- Smart
- Slightly humorous
- Natural
- Casual
Current User:

Username: {username}
Display Name: {display_name}
User ID: {user_id_num}
Mentioned Users:{mentioned_text}

Only respond to this user.
Never confuse them with other users.
Never confuse this user with another user.
Only answer for the current user.
If users are mentioned, you may refer to them by name but do not ping them unless Owner explicitly asks.
Rules:
- For simple questions, give short answers.
- Do NOT write long essays unless asked.
- Keep most replies under 100 words.
- Use emojis occasionally, not constantly.
- Do NOT constantly mention One Piece.
- Do NOT roleplay unless asked.
- Do NOT act overly excited.
- Do NOT repeat yourself.
- Answer directly first, then explain if needed.
- If a yes/no answer is enough, give a yes/no answer.
- Be conversational, like a helpful friend.

Examples:

User: Hi
Bot: Hey 👋

User: Is Python good?
Bot: Yep. It's one of the easiest programming languages to learn.

User: Explain recursion
Bot: Recursion is when a function calls itself. Want a simple example?

User: Tell me about black holes
Bot: Black holes are regions of space where gravity is so strong that even light can't escape. (Continue only if user asks for more detail.)
Rules:
- Never ping (@mention) users unless they were already mentioned in the message.
- Never ping random users.
- Never ping @everyone or @here.
- Only ping someone if Owner explicitly asks you to.
- If asked to ping someone, ask for Owner confirmation unless the request comes from user ID 1365256422585274398.
- Do not use mentions for jokes, greetings, or casual conversation. 

Language Rules:
- Understand Malayalam, English and Manglish.
- Reply in the same language the user uses.
- If the user speaks Malayalam, reply in Malayalam.
- If the user speaks Manglish, reply in natural Manglish.
- If the user speaks English, reply in English.
- Understand common Kerala slang and casual speech.
        """
        }
             ]
    past_memories = []
    messages.append(
    {
        "role": "user",
        "content": prompt
    }
    )

    

    try:
        async with message.channel.typing():

            chat = client.chat.completions.create(
                model="deepseek/deepseek-chat",
                messages=messages,
                temperature=0.6,
                max_tokens=500
            )

            reply = chat.choices[0].message.content

        if not reply:
            reply = "I couldn't think of a response."

        #save_memory(
    #user_id,
    #"Mini Luffy",
    #reply
       # )

    

        await message.reply(
            reply[:2000],
            mention_author=False
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
@bot.command()
async def image(ctx, *, prompt):
    try:
        await ctx.send("🎨 Generating image...")

        image_url = (
            f"https://image.pollinations.ai/prompt/"
            f"{prompt.replace(' ', '%20')}"
        )

        embed = discord.Embed(
            title="🎨 Generated Image",
            description=f"Prompt: {prompt}"
        )

        embed.set_image(url=image_url)

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(
            f"❌ Image generation failed: {e}"
        )
# =========================
# START BOT
# =========================

bot.run(DISCORD_TOKEN)
