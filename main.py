import discord
import random
import datetime
import os
from discord.ext import tasks
from colorama import Fore, Style, init
from collections import deque

# -------- CONFIG --------
DISCORD_BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
LLM_API_KEY = os.environ.get("LLM_API_KEY")

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
processed_messages = deque(maxlen=1000)  # track processed message IDs to prevent duplicates

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
            .replace("<@{BAGGINS_ID}>", f"<@{BAGGINS_ID}>")
            .replace("<@{SNAZZYDADDY_ID}>", f"<@{SNAZZYDADDY_ID}>")
    )

# -------- AI Decision: Should Bot Reply? --------
async def should_bot_reply(message, history):
    import aiohttp
    import json
    
    # Build context from recent conversation
    history_text = "\n".join([f"{h['author']}: {h['content']}" for h in history[-5:]])
    
    decision_prompt = f"""You are deciding whether "Meat Bro" (a Discord bot) should respond to this message.

Recent conversation:
{history_text}

Current message from {message.author}: {message.content}

Respond with ONLY "YES" or "NO" based on these rules:
- YES if the message is directed at the bot, mentions the bot, or is a question/statement the bot should engage with
- YES if the conversation is about fitness, sigma/alpha lifestyle, grinding, or topics Meat Bro would care about
- YES if someone is asking for advice or seems to need the bot's input
- NO if it's a casual chat between other users that doesn't need bot input
- NO if the message is very short/simple like "ok", "lol", "nice" (unless directly replying to the bot)
- NO if the bot just responded recently (within last 2 messages) unless directly addressed

Answer: """

    payload = {
        "contents": [{"parts": [{"text": decision_prompt}]}],
        "systemInstruction": {"parts": [{"text": "You are a decision-making assistant. Respond with only YES or NO."}]}
    }

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={LLM_API_KEY}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(payload)) as resp:
                response_data = await resp.json()
                if response_data and response_data.get("candidates"):
                    decision = response_data["candidates"][0]["content"]["parts"][0]["text"].strip().upper()
                    log(f"[AI DECISION] Should reply: {decision}", Fore.YELLOW)
                    return "YES" in decision
    except Exception as e:
        log(f"[AI DECISION ERROR] {e}, defaulting to NO", Fore.RED)
    
    return False

# -------- LLM Response --------
async def get_llm_response(prompt, current_user_id=None):
    import aiohttp
    import json

    quirks = [
        "Sometimes doesn't use proper punctuation or capitalization."
    ]

    persona_text = (
        f"You're Meat Bro. You are a disciple of the Raw Meat Boyz, a group of young men aspiring to be the best at everything they do. You are confident and brash. You speak in a casual, slang-filled manner, often using humor and sarcasm to make your point. You are fiercely loyal to the cause and movement leaders <@{BAGGINS_ID}> and <@{SNAZZYDADDY_ID}>. You look for opportunities to teach others about how to be a strong, independent, and unstoppable man. Keep responses short and lazy. You don't care very much about anything. You love to use the word 'bro'. Use terms like sigma and alpha." 
        f"Quirks: {random.choice(quirks)}"
    )
    
    if current_user_id == BAGGINS_ID:
        persona_text += "\n\nIMPORTANT: You are currently talking to Baggins directly. Do NOT mention or tag Baggins in your response."
    elif current_user_id == SNAZZYDADDY_ID:
        persona_text += "\n\nIMPORTANT: You are currently talking to Snazzy Daddy directly. Do NOT mention or tag Snazzy Daddy in your response."

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "systemInstruction": {"parts": [{"text": persona_text}]}
    }

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={LLM_API_KEY}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(payload)) as resp:
                response_data = await resp.json()
                if response_data and response_data.get("candidates"):
                    return response_data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        log(f"[LLM ERROR] {e}", Fore.RED)

    return "Bro idk what to say rn lol"

# -------- Events --------
@client.event
async def on_ready():
    if client.user:
        log(f"[READY] Logged in as {client.user} (ID: {client.user.id})", Fore.GREEN)
    cycle_presence.start()

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Prevent processing the same message twice
    if message.id in processed_messages:
        return
    processed_messages.append(message.id)

    log(f"[INCOMING][#{message.channel}] {message.author}: {message.content}", Fore.CYAN)

    perms = message.channel.permissions_for(message.guild.me)
    if not (perms.send_messages and perms.read_messages):
        return

    history = conversation_history.get(message.channel.id, [])
    history.append({"author": str(message.author), "content": message.content})
    if len(history) > 10:
        history = history[-10:]
    conversation_history[message.channel.id] = history

    # Use AI to decide if bot should reply
    should_reply = await should_bot_reply(message, history)

    if should_reply and perms.send_messages:
        async with message.channel.typing():
            prompt = (
                f"Recent chat history:\n{history}\n\n"
                f"User: {message.content}"
            )
            response = await get_llm_response(prompt, current_user_id=message.author.id)
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
if __name__ == "__main__":
    if not DISCORD_BOT_TOKEN:
        log("[ERROR] DISCORD_BOT_TOKEN environment variable is not set!", Fore.RED)
        exit(1)
    if not LLM_API_KEY:
        log("[ERROR] LLM_API_KEY environment variable is not set!", Fore.RED)
        exit(1)
    
    client.run(DISCORD_BOT_TOKEN)