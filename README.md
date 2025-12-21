# Meat Bro Discord Bot

## Overview
This is a Discord bot named "Meat Bro" that embodies the persona of a confident, brash disciple of the "Raw Meat Boyz" movement. The bot uses Google's Gemini LLM API to generate responses and interacts with Discord users in a casual, slang-filled manner.

## Features
- **AI-Powered Response Decision**: Uses AI to intelligently decide when to respond based on message context, conversation history, and relevance
- **Smart User Recognition**: Detects when talking to specific users and avoids mentioning them to themselves
- **LLM-Powered Responses**: Uses Google Gemini 2.5 Flash to generate contextual responses
- **Conversation Memory**: Maintains short-term memory per channel (last 10 messages)
- **Dynamic Status**: Changes bot status every hour with random AI-generated messages
- **Colorful Logging**: Uses colorama for timestamped, color-coded console logs with AI decision tracking

## Prerequisites

### 1. Python
- Python 3.11 or higher
- You can download Python from [python.org](https://www.python.org/downloads/)

### 2. API Keys
You'll need to obtain the following API keys:

- **Discord Bot Token**: 
  1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
  2. Create a new application or select an existing one
  3. Go to the "Bot" section
  4. Click "Reset Token" to get your bot token
  5. Enable "Message Content Intent" under Privileged Gateway Intents

- **Google Gemini API Key**:
  1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
  2. Sign in with your Google account
  3. Click "Create API Key"
  4. Copy the generated API key

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Meat-Bot
```

### 2. Create a Virtual Environment (Recommended)
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

#### Option A: Using a .env file (Recommended)
1. Copy the example file:
   ```bash
   # On Windows
   copy .env.example .env
   
   # On macOS/Linux
   cp .env.example .env
   ```

2. Edit the `.env` file with your favorite text editor and add your API keys:
   ```
   DISCORD_BOT_TOKEN=your_discord_bot_token_here
   LLM_API_KEY=your_gemini_api_key_here
   ```

3. Install python-dotenv to load the .env file:
   ```bash
   pip install python-dotenv
   ```

#### Option B: Set environment variables manually
```bash
# On Windows (Command Prompt)
set DISCORD_BOT_TOKEN=your_discord_bot_token_here
set LLM_API_KEY=your_gemini_api_key_here

# On Windows (PowerShell)
$env:DISCORD_BOT_TOKEN="your_discord_bot_token_here"
$env:LLM_API_KEY="your_gemini_api_key_here"

# On macOS/Linux
export DISCORD_BOT_TOKEN=your_discord_bot_token_here
export LLM_API_KEY=your_gemini_api_key_here
```

## Running the Bot

### Method 1: Direct Python Execution
```bash
python bot.py
```

### Method 2: Using the Run Script (Windows)
```bash
run.bat
```

### Method 3: Using the Run Script (macOS/Linux)
```bash
./run.sh
```

The bot will start and connect to Discord. You should see colorful log messages in your terminal indicating the bot is ready.

## Project Structure

```
Meat-Bot/
├── bot.py              # Core bot logic and Discord event handlers
├── config.py           # Configuration settings and API keys
├── llm.py             # LLM integration for AI responses
├── utils.py           # Utility functions for logging and mentions
├── requirements.txt   # Python dependencies
├── .env.example       # Example environment variables file
├── .env              # Your actual environment variables (not tracked by git)
└── README.md         # This file
```

## Configuration

### Bot Behavior
The bot's behavior can be customized in `config.py`:
- `PERSONA_TEXT`: Defines the bot's personality and response style
- `ALL_STATUSES`: List of possible bot status messages
- `BAGGINS_ID` and `SNAZZYDADDY_ID`: User IDs for special mention handling

### Reply Decision System
The bot uses a conservative AI-powered system that defaults to NOT responding unless:
- The message is a direct reply to the bot
- The message mentions "Meat Bro" or tags the bot
- The AI determines the message clearly asks for bot input

## Troubleshooting

### "DISCORD_BOT_TOKEN environment variable is not set!"
- Make sure you've set up your environment variables correctly
- If using a .env file, ensure python-dotenv is installed and the file is in the same directory as bot.py

### "LLM_API_KEY environment variable is not set!"
- Verify your Gemini API key is set in the environment variables or .env file

### Bot doesn't respond to messages
- Check that "Message Content Intent" is enabled in the Discord Developer Portal
- Verify the bot has proper permissions in your Discord server (Read Messages, Send Messages)

### Import errors
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Verify you're using Python 3.11 or higher

## Running on Replit

This bot can also be run on Replit. The repository includes Replit-specific configuration files (`.replit` and `replit.md`). Simply:
1. Import the repository to Replit
2. Set the environment variables in Replit Secrets
3. Click the Run button

## Security Notes
- Never commit your `.env` file to version control
- Keep your API keys secret and never share them
- The `.gitignore` file is configured to prevent accidentally committing sensitive files

## License
This project is provided as-is for personal use.
