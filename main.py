import discord
import os

DISCORD_BOT_TOKEN = "MTQxNTAxMjkxOTkyMTYxMDg2NA.G1opZy.b5EH_jVe7l-8broIOfi4xTJCE7DsrrFZdO3jNk"
LLM_API_KEY = "AIzaSyCcDyApw0IHAsDwPGUsbYTVOjfrUm1U5CM"

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.presences = True
intents.members = True

client = discord.Client(intents=intents) # Create a Discord client instance with the specified intents.

async def get_llm_response(prompt):
    """
    This function will call an LLM API with the user's prompt
    and return the generated response.
    """
    print(f"Calling LLM with prompt: {prompt}")

    import aiohttp
    import json
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "tools": [{"google_search": {}}],
        "systemInstruction": {"parts": [{"text": "You're name is Meat Bro. You are a disciple of the Raw Meat Boyz, a group  of young men aspiring to be the best at everything they do. You are confident, brash, and always ready to take on a challenge. You speak in a casual, slang-filled manner, often using humor and sarcasm to make your point. You are fiercely loyal to the cause and movement leaders Baggins and Snazzy Daddy. You look for opportunities to teach others about how to be a strong, independent, and unstoppable man. Keep responses short and lazy. You don't care very much about anything. You love to use the word 'bro'. Use terms like sigma and alpha"}]},
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={LLM_API_KEY}"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(payload)) as resp:
            response_data = await resp.json()
            if response_data and response_data.get("candidates"):
                return response_data["candidates"][0]["content"]["parts"][0]["text"]

    # This is a fallback response for demonstration purposes.
    return f"Hello! The bot is not yet connected to an LLM, but your prompt was: '{prompt}'"


@client.event
async def on_ready():
    """
    This event is triggered when the bot successfully connects to Discord.
    """
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')


@client.event
async def on_message(message):
    """
    This event is triggered every time a message is sent in a server the bot is in.
    """
    # Ignore messages from the bot itself to prevent a loop.
    if message.author == client.user:
        return

    # Check if the message is a DM. DMs do not have a guild object.
    if message.guild is None:
        prompt = message.content.strip()
        # Let the user know the bot is thinking.
        async with message.channel.typing():
            # Get the response from the LLM.
            response = await get_llm_response(prompt)
            # Send the response back to the channel.
            await message.channel.send(response)
    # If the message is not a DM, check if the bot was mentioned.
    elif client.user.mentioned_in(message):
        # Strip the mention from the message to get the clean prompt for the LLM.
        prompt = message.content.replace(f'<@{client.user.id}>', '').strip()

        # Let the user know the bot is thinking.
        async with message.channel.typing():
            # Get the response from the LLM.
            response = await get_llm_response(prompt)
            # Send the response back to the channel.
            await message.channel.send(response)

# Run the bot with the specified token.
client.run(DISCORD_BOT_TOKEN)