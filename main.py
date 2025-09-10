import discord
import os
import random
import asyncio
from discord.ext import tasks

DISCORD_BOT_TOKEN = "YOUR_DISCORD_BOT_TOKEN"
LLM_API_KEY = "YOUR_GEMINI_API_KEY"

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

    # Keep short history per channel
    history = conversation_history.get(message.channel.id, [])
    history.append({"author": str(message.author), "content": message.content})
    if len(history) > 10:
        history = history[-10:]
    conversation_history[message.channel.id] = history

    should_reply = False

    # Always reply if mentioned
    if client.user.mentioned_in(message):
        should_reply = True
    # Random chance to reply (feels alive)
    elif random.random() < 0.08:  # ~8% chance
        should_reply = True
    # Trigger words
    elif any(word in message.content.lower() for word in ["bro", "sigma", "alpha", "gym", "grind"]):
        should_reply = True

    if should_reply:
        async with message.channel.typing():
            await asyncio.sleep(random.uniform(1, 3))  # typing delay
            prompt = (
                f"Recent chat history:\n{history}\n\n"
                f"User: {message.content}\nBot:"
            )
            response = await get_llm_response(prompt)
            await message.channel.send(response)

    # Random emoji reactions to spice things up
    if random.random() < 0.05:  # 5% chance
        emojis = ["💪", "🔥", "😂", "😎", "🍖"]
        await message.add_reaction(random.choice(emojis))


# -------- Scheduled Background Chatter --------
@tasks.loop(minutes=30)  # every 30 minutes
async def random_chatter():
    if not client.guilds:
        return
    guild = random.choice(client.guilds)
    if not guild.text_channels:
        return
    channel = random.choice(guild.text_channels)
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