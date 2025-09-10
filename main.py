import discord
import random
import asyncio
from discord.ext import commands

DISCORD_BOT_TOKEN = "MTQxNTAxMjkxOTkyMTYxMDg2NA.G1opZy.b5EH_jVe7l-8broIOfi4xTJCE7DsrrFZdO3jNk"
LLM_API_KEY = "AIzaSyCcDyApw0IHAsDwPGUsbYTVOjfrUm1U5CM"

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.presences = True
intents.members = True

client = discord.Client(intents=intents)

conversation_history = {}  # short memory per channel

# -------- LLM Response --------
async def get_llm_response(prompt):
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
        async with session.post(
            url, headers={"Content-Type": "application/json"}, data=json.dumps(payload)
        ) as resp:
            response_data = await resp.json()
            if response_data and response_data.get("candidates"):
                return response_data["candidates"][0]["content"]["parts"][0]["text"]

    return f"Bro idk what to say rn lol (debug: {prompt})"


# -------- Events --------
@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')
    client.loop.create_task(random_chatter())  # background chatter


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Log all incoming messages
    print(f"[INCOMING] {message.author}: {message.content}")

    # Check channel perms
    perms = message.channel.permissions_for(message.guild.me)
    if not (perms.send_messages and perms.read_messages):
        return

    # Store conversation history
    history = conversation_history.get(message.channel.id, [])
    history.append({"author": str(message.author), "content": message.content})
    if len(history) > 10:
        history = history[-10:]
    conversation_history[message.channel.id] = history

    should_reply = False
    if client.user.mentioned_in(message):
        should_reply = True
    elif random.random() < 0.08:  # ~8% chance
        should_reply = True
    elif any(word in message.content.lower() for word in ["bro", "sigma", "alpha", "gym", "grind"]):
        should_reply = True

    if should_reply and perms.send_messages:
        async with message.channel.typing():
            await asyncio.sleep(random.uniform(1, 3))
            prompt = f"Recent chat history:\n{history}\n\nUser: {message.content}\nBot:"
            response = await get_llm_response(prompt)

            print(f"[OUTGOING] {client.user}: {response}")
            await message.channel.send(response)

    # Random emoji reactions
    if perms.add_reactions and random.random() < 0.05:
        emojis = ["💪", "🔥", "😂", "😎", "🍖"]
        chosen = random.choice(emojis)
        print(f"[REACTION] Added {chosen} to {message.author}'s message")
        await message.add_reaction(chosen)


# -------- Random Background Chatter --------
async def random_chatter():
    await client.wait_until_ready()
    while not client.is_closed():
        # random wait time 10–60 minutes
        wait_time = random.randint(600, 3600)
        await asyncio.sleep(wait_time)

        if not client.guilds:
            continue

        # 50% chance to skip
        if random.random() > 0.5:
            continue

        guild = random.choice(client.guilds)
        allowed_channels = [
            c for c in guild.text_channels
            if c.permissions_for(guild.me).send_messages
        ]
        if not allowed_channels:
            continue

        channel = random.choice(allowed_channels)
        try:
            async with channel.typing():
                await asyncio.sleep(random.uniform(5, 60))  # human-like delay
                starter_lines = [
                    "Yo bros what’s the grind today?",
                    "Anyone hitting the gym or what?",
                    "Bro I’m feeling alpha rn 💪",
                    "Sigma mindset only today 🔥",
                    "What’s good fam?"
                ]
                msg = random.choice(starter_lines)
                print(f"[OUTGOING] {client.user} (random chatter): {msg}")
                await channel.send(msg)
        except Exception as e:
            print(f"Chatter error: {e}")

# -------- Run Bot --------
client.run(DISCORD_BOT_TOKEN)