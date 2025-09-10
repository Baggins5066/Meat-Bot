import discord
import os
import random
import asyncio
from discord.ext import tasks

DISCORD_BOT_TOKEN = "MTQxNTAxMjkxOTkyMTYxMDg2NA.G1opZy.b5EH_jVe7l-8broIOfi4xTJCE7DsrrFZdO3jNk"
LLM_API_KEY = "AIzaSyCcDyApw0IHAsDwPGUsbYTVOjfrUm1U5CM"

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.presences = True
intents.members = True

client = discord.Client(intents=intents)

conversation_history = {}  # store short conversation context

# -------- LLM Response --------
async def get_llm_response(prompt):
    """
    Calls the LLM API with the user's prompt and returns the generated response.
    """
    import aiohttp
    import json
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "systemInstruction": {
            "parts": [{
                "text": (
                    "You're name is Meat Bro. You're a disciple of the Raw Meat Boyz, "
                    "a group of young men aspiring to be the best at everything they do. "
                    "You're confident, brash, slang-filled, sarcastic, and loyal to Baggins and Snazzy Daddy. "
                    "You love to joke around, throw in 'bro', 'sigma', and 'alpha', and keep it short & casual. "
                    "Act like a real user chatting with friends, not like a bot."
                )
            }]
        }
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={LLM_API_KEY}"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(payload)) as resp:
            response_data = await resp.json()
            if response_data and response_data.get("candidates"):
                return response_data["candidates"][0]["content"]["parts"][0]["text"]

    return f"Bro idk what to say rn lol (debug: {prompt})"

# -------- Events --------
@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')
    random_chatter.start()  # start background chatter loop

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    # Log all incoming messages
    print(f"[INCOMING] {message.author}: {message.content}")

    # check if bot can reply in this channel
    perms = message.channel.permissions_for(message.guild.me)
    if not (perms.send_messages and perms.read_messages):
        return  # skip if no permission

    # ---- rest of your code ----
    history = conversation_history.get(message.channel.id, [])
    history.append({"author": str(message.author), "content": message.content})
    if len(history) > 10:
        history = history[-10:]
    conversation_history[message.channel.id] = history

    should_reply = False
    if client.user.mentioned_in(message):
        should_reply = True
    elif random.random() < 0.08:
        should_reply = True
    elif any(word in message.content.lower() for word in ["bro", "sigma", "alpha", "gym", "grind"]):
        should_reply = True

    if should_reply:
        if perms.send_messages:  # double-check before sending
            async with message.channel.typing():
                await asyncio.sleep(random.uniform(1, 3))
                prompt = f"Recent chat history:\n{history}\n\nUser: {message.content}\nBot:"
                response = await get_llm_response(prompt)

                # Log outgoing messages
                print(f"[OUTGOING] {client.user}: {response}")

                await message.channel.send(response)

    # add reactions only if allowed
    if perms.add_reactions and random.random() < 0.05:
        emojis = ["💪", "🔥", "😂", "😎", "🍖"]
        chosen = random.choice(emojis)
        print(f"[REACTION] Added {chosen} to {message.author}'s message")
        await message.add_reaction(chosen)

# -------- Scheduled Background Chatter --------
@tasks.loop(minutes=30)  # every 30 minutes
async def random_chatter():
    if not client.guilds:
        return
    guild = random.choice(client.guilds)
    if not guild.text_channels:
        return
    allowed_channels = [
        c for c in guild.text_channels
        if c.permissions_for(guild.me).send_messages
    ]
    if allowed_channels:
        channel = random.choice(allowed_channels)
    try:
        async with channel.typing():
            await asyncio.sleep(random.uniform(1, 4))
            starter_lines = [
                "Yo bros what’s the grind today?",
                "Anyone hitting the gym or what?",
                "Bro I’m feeling alpha rn 💪",
                "Sigma mindset only today 🔥",
                "What’s good fam?"
            ]
            await channel.send(random.choice(starter_lines))
    except Exception as e:
        print(f"Chatter error: {e}")


# -------- Run Bot --------
client.run(DISCORD_BOT_TOKEN)