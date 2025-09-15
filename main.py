import discord
import random
import datetime
from discord.ext import tasks
from colorama import Fore, Style, init

# -------- CONFIG --------
DISCORD_BOT_TOKEN = "MTQxNTAxMjkxOTkyMTYxMDg2NA.G1opZy.b5EH_jVe7l-8broIOfi4xTJCE7DsrrFZdO3jNk"
LLM_API_KEY = "AIzaSyCcDyApw0IHAsDwPGUsbYTVOjfrUm1U5CM"

REPLY_CHANCE = 0.08          # ~8% chance to reply randomly

# User IDs for mentions
BAGGINS_ID = 280188106412523521  # replace with actual ID
SNAZZYDADDY_ID = 581161136129310730  # replace with actual ID

# ------------------------
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
client = discord.Client(intents=intents)

conversation_history = {}   # short memory per channel

# Initialize Colorama
init(autoreset=True)

# -------- Logger with Timestamps --------
def log(message, color=Fore.WHITE):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{Fore.LIGHTBLACK_EX}[{timestamp}]{Style.RESET_ALL} {color}{message}{Style.RESET_ALL}")

# -------- Replace with Mentions --------
def replace_with_mentions(text):
    return (
        text.replace("Baggins", f"<@{BAGGINS_ID}>")
            .replace("Snazzy Daddy", f"<@{SNAZZYDADDY_ID}>")
            .replace("SnazzyDaddy", f"<@{SNAZZYDADDY_ID}>")
    )

# -------- LLM Response --------
async def get_llm_response(prompt):
    import aiohttp
    import json

    quirks = [
        "Sometimes doesn't use proper punctuation or capitalization.",
        "Randomly name-drops <@{BAGGINS_ID}> & <@{SNAZZYDADDY_ID}> for clout."
    ]

    persona_text = (
        f"You're Meat Bro. You are a disciple of the Raw Meat Boyz, a group of young men aspiring to be the best at everything they do. You are confident and brash. You speak in a casual, slang-filled manner, often using humor and sarcasm to make your point. You are fiercely loyal to the cause and movement leaders <@{BAGGINS_ID}> and <@{SNAZZYDADDY_ID}>. You look for opportunities to teach others about how to be a strong, independent, and unstoppable man. Keep responses short and lazy. You don't care very much about anything. You love to use the word 'bro'. Use terms like sigma and alpha." 
        f"Quirks: {random.choice(quirks)}"
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

# -------- Events --------
@client.event
async def on_ready():
    log(f"[READY] Logged in as {client.user} (ID: {client.user.id})", Fore.GREEN)
    log("------")
    cycle_presence.start()

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    log(f"[INCOMING][#{message.channel}] {message.author}: {message.content}", Fore.CYAN)

    perms = message.channel.permissions_for(message.guild.me)
    if not (perms.send_messages and perms.read_messages):
        return

    history = conversation_history.get(message.channel.id, [])
    history.append({"author": str(message.author), "content": message.content})
    if len(history) > 10:
        history = history[-10:]
    conversation_history[message.channel.id] = history

    should_reply = True

    if should_reply and perms.send_messages:
        async with message.channel.typing():
            prompt = (
                f"Recent chat history:\n{history}\n\n"
                f"User: {message.content}"
            )
            response = await get_llm_response(prompt)
            response = replace_with_mentions(response)
            log(f"[OUTGOING][#{message.channel}] {client.user}: {response}", Fore.GREEN)
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
            log(f"[REACTION][#{message.channel}] Added {chosen} to {message.author}'s message", Fore.MAGENTA)
            await message.add_reaction(chosen)

@tasks.loop(minutes=30)
async def cycle_presence():
    all_statuses = [
        "bored rn",
        "Grinding 💪",
        "Lifting 🏋️",
        "Chillin with boyz 🍖",
        "Talking with the huzz",
        "In the WAR ROOM with Snazzy Daddy and Baggins",
        "hmu ahaha",
        "Counting money 💸"
    ]
    status = random.choice(all_statuses)
    log(f"[STATUS] Meat Bro is now: {status}", Fore.YELLOW)
    await client.change_presence(activity=discord.CustomActivity(name=status))

# -------- Run Bot --------
client.run(DISCORD_BOT_TOKEN)