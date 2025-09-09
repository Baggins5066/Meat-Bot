import discord
import os

# --- IMPORTANT ---
# You need to replace the placeholder with your actual Discord bot token.
# Keep this token secret and do not share it.
DISCORD_BOT_TOKEN = "YOUR_DISCORD_BOT_TOKEN"

# You'll also need an API key for a Large Language Model.
# Replace this placeholder with your actual key.
LLM_API_KEY = "YOUR_LLM_API_KEY"

# The following intents are required for the bot to receive messages.
# The 'message_content' intent is privileged and must be enabled in the Discord Developer Portal.
intents = discord.Intents.default()
intents.message_content = True

# Create a Discord client instance with the specified intents.
client = discord.Client(intents=intents)

# This function is a placeholder for your LLM API call.
# You will need to replace the logic inside this function to
# call your chosen LLM and return its response.
async def get_llm_response(prompt):
    """
    This function will call an LLM API with the user's prompt
    and return the generated response.
    """
    print(f"Calling LLM with prompt: {prompt}")

    # TODO: Replace the following with your actual API call to the LLM.
    # For example, using the Gemini API.
    # The `gemini-2.5-flash-preview-05-20` model is recommended for its speed.
    # The `Google Search` tool can be used for grounded responses.
    
    # Example using Gemini API (uncomment and fill in with your key and logic)
    # import json
    # payload = {
    #     "contents": [{"parts": [{"text": prompt}]}],
    #     "tools": [{"google_search": {}}],
    #     "systemInstruction": {"parts": [{"text": "You are a helpful and friendly chat bot."}]}
    # }
    # url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={LLM_API_KEY}"
    # async with aiohttp.ClientSession() as session:
    #     async with session.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(payload)) as resp:
    #         response_data = await resp.json()
    #         if response_data and response_data.get("candidates"):
    #             return response_data["candidates"][0]["content"]["parts"][0]["text"]

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

    # Check if the bot was mentioned in the message.
    if client.user.mentioned_in(message):
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