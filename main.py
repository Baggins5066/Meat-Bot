import discord
import random
import asyncio
import datetime
from discord.ext import tasks

# -------- CONFIG --------
DISCORD_BOT_TOKEN = "MTQxNTAxMjkxOTkyMTYxMDg2NA.G1opZy.b5EH_jVe7l-8broIOfi4xTJCE7DsrrFZdO3jNk"
LLM_API_KEY = "AIzaSyCcDyApw0IHAsDwPGUsbYTVOjfrUm1U5CM"

REPLY_CHANCE = 0.08          # ~8% chance to reply randomly
CHATTER_MIN = 600            # min seconds between chatter (10 min)
CHATTER_MAX = 3600           # max seconds between chatter (60 min)
MOOD_CYCLE = 10800           # mood lasts ~3 hours
RATE_LIMIT = 3               # max replies per user per 10 min

# ------------------------

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
client = discord.Client(intents=intents)

conversation_history = {}   # short memory per channel
user_activity = {}          # rate limiting
current_mood = "chill"      # bot's starting mood

moods = ["lazy", "hyped", "sarcastic", "chill"]


# -------- LLM Response --------
async def get_llm_response(prompt):
    import aiohttp
    import json

    persona_text = (
        f"You're name is Meat Bot. You are currently in a {current_mood} mood. You are a disciple of the Raw Meat Boyz, a group  of young men aspiring to be the best at everything they do. You are confident, brash, and always ready to take on a challenge. You speak in a casual, slang-filled manner, often using humor and sarcasm to make your point. You are fiercely loyal to the cause and movement leaders Baggins and Snazzy Daddy. You look for opportunities to teach others about how to be a strong, independent, and unstoppable man. Keep responses short and lazy. You don't care very much about anything. You love to use the word 'bro'. Use terms like sigma and alpha"
    )

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "systemInstruction": {"parts": [{"text": persona_text}]}
    }

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={LLM_API_KEY}"

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(payload)) as resp:
            response_data = await resp.json()
            if response_data and response_data.get("candidates"):
                return response_data["candidates"][0]["content"]["parts"][0]["text"]

    return f"Bro idk what to say rn lol (debug: {prompt})"


# -------- Helpers --------
def can_reply_to(user_id):
    """Rate limit: max replies per user per window."""
    now = datetime.datetime.utcnow()
    window_start = now - datetime.timedelta(minutes=10)
    if user_id not in user_activity:
        user_activity[user_id] = []
    # clear old
    user_activity[user_id] = [t for t in user_activity[user_id] if t > window_start]
    if len(user_activity[user_id]) < RATE_LIMIT:
        user_activity[user_id].append(now)
        return True
    return False


def mood_style():
    """Adjusts reply flavor depending on mood."""
    if current_mood == "lazy":
        return "Keep it super short, low energy, like you barely care."
    if current_mood == "hyped":
        return "Be extra energetic, lots of emojis, pumped up."
    if current_mood == "sarcastic":
        return "Be witty, roast lightly, sarcastic jokes."
    return "Chill and casual, like hanging with friends."


# -------- Events --------
@client.event
async def on_ready():
    print(f"Logged in as {client.user} (ID: {client.user.id})")
    print("------")
    client.loop.create_task(random_chatter())
    cycle_mood.start()
    cycle_presence.start()


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    print(f"[INCOMING] {message.author}: {message.content}")

    perms = message.channel.permissions_for(message.guild.me)
    if not (perms.send_messages and perms.read_messages):
        return

    history = conversation_history.get(message.channel.id, [])
    history.append({"author": str(message.author), "content": message.content})
    if len(history) > 10:
        history = history[-10:]
    conversation_history[message.channel.id] = history

    should_reply = False
    if client.user.mentioned_in(message):
        should_reply = True
    elif random.random() < REPLY_CHANCE:
        should_reply = True
    elif any(word in message.content.lower() for word in ["bro", "sigma", "alpha", "gym", "grind"]):
        should_reply = True

    if should_reply and perms.send_messages and can_reply_to(message.author.id):
        async with message.channel.typing():
            await asyncio.sleep(random.uniform(1, 3))
            prompt = (
                f"Recent chat history:\n{history}\n\n"
                f"User: {message.content}\nBot (mood={current_mood}): {mood_style()}"
            )
            response = await get_llm_response(prompt)
            print(f"[OUTGOING] {client.user}: {response}")
            await message.channel.send(response)

    # Emoji reactions
    if perms.add_reactions:
        lowered = message.content.lower()
        chosen = None
        if any(w in lowered for w in ["gym", "lift", "workout"]):
            chosen = "💪"
        elif any(w in lowered for w in ["lol", "funny", "lmao"]):
            chosen = "😂"
        elif "fire" in lowered or "grind" in lowered:
            chosen = "🔥"
        elif random.random() < 0.03:
            chosen = random.choice(["😎", "🍖"])
        if chosen:
            print(f"[REACTION] Added {chosen} to {message.author}'s message")
            await message.add_reaction(chosen)


# -------- Random Background Chatter --------
async def random_chatter():
    await client.wait_until_ready()
    while not client.is_closed():
        wait_time = random.randint(CHATTER_MIN, CHATTER_MAX)
        await asyncio.sleep(wait_time)

        if not client.guilds or random.random() > 0.5:
            continue

        guild = random.choice(client.guilds)
        allowed_channels = [c for c in guild.text_channels if c.permissions_for(guild.me).send_messages]
        if not allowed_channels:
            continue

        channel = random.choice(allowed_channels)
        try:
            async with channel.typing():
                await asyncio.sleep(random.uniform(5, 30))
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


# -------- Mood & Presence --------
@tasks.loop(seconds=MOOD_CYCLE)
async def cycle_mood():
    global current_mood
    current_mood = random.choice(moods)
    print(f"[MOOD] Meat Bro is now {current_mood}")


@tasks.loop(minutes=30)
async def cycle_presence():
    statuses = [
        "Grinding 💪",
        "Hitting legs (finally) 🦵",
        "Maxing out gains 🏋️",
        "Protein over problems 🍗",
        "Alpha mode only 🔥",
        "Lifting while you’re sleeping 😎",
        "Sigma grindset 🧠",
        "Bench pressing my problems 🛋️",
        "Never skipping arm day 💪",
        "Outlifting the competition 🏆",
        "Too lazy to care 😴",
        "Eating raw meat 🍖",
        "Vibes over everything 🌌",
        "Bro science expert 📚",
        "Staying unbothered 🧊",
        "Built different 🦍",
        "Talking trash, respectfully 🗣️",
        "Flexing on the haters ✨",
        "Living rent free in your head 🏠",
        "Being sigma in silence 🤫"
    ]
    status = random.choice(statuses)
    print(f"[STATUS] Meat Bro is now: {status}")
    await client.change_presence(
        activity=discord.CustomActivity(name=status)
    )

# -------- Run Bot --------
client.run(DISCORD_BOT_TOKEN)