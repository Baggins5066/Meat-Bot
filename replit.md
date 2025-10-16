# Meat Bro Discord Bot

## Overview
This is a Discord bot named "Meat Bro" that embodies the persona of a confident, brash disciple of the "Raw Meat Boyz" movement. The bot uses Google's Gemini LLM API to generate responses and interacts with Discord users in a casual, slang-filled manner.

## Project Status
✅ **Setup Complete** - Discord bot ready to run after API keys are configured

## Recent Changes
- **2025-10-16**: Added AI-powered response decision system
  - Bot now uses AI to intelligently decide whether to respond to messages
  - Considers conversation context, message content, and recent interactions
  - Prevents spam by avoiding responses to casual chatter that doesn't need bot input
  - New `should_bot_reply()` function analyzes each message before responding
- **2025-10-15**: Initial Replit environment setup
  - Migrated hardcoded API keys to environment variables for security
  - Created requirements.txt for dependency management
  - Set up Discord Bot workflow
  - Added .gitignore for Python and sensitive files
  - Added error handling for missing API keys

## Features
- **AI-Powered Response Decision**: Uses AI to intelligently decide when to respond based on message context, conversation history, and relevance
- **LLM-Powered Responses**: Uses Google Gemini 2.5 Flash to generate contextual responses
- **Conversation Memory**: Maintains short-term memory per channel (last 10 messages)
- **Emoji Reactions**: Automatically reacts to messages with relevant emojis
- **Dynamic Status**: Changes bot status every 30 minutes with random messages
- **Colorful Logging**: Uses colorama for timestamped, color-coded console logs with AI decision tracking

## Project Architecture

### Main Components
- **main.py**: Core bot logic including Discord event handlers, LLM integration, and message processing
- **requirements.txt**: Python dependencies (discord.py, colorama, aiohttp)

### Dependencies
- `discord.py` (v2.6+): Discord API integration
- `colorama` (v0.4.6+): Terminal color formatting
- `aiohttp` (v3.13+): Async HTTP requests to Gemini API

### Environment Variables Required
- `DISCORD_BOT_TOKEN`: Discord bot authentication token
- `LLM_API_KEY`: Google Gemini API key

### Bot Configuration
- **Reply Decision**: AI-powered decision system analyzes messages to determine if bot should respond
- **Reply Rules**: Bot responds when:
  - Message is directed at the bot or mentions it
  - Conversation is about fitness, sigma/alpha lifestyle, or topics Meat Bro cares about
  - Someone is asking for advice or needs bot input
  - Avoids responding to casual chat between other users or simple acknowledgments
- **User IDs**: Hardcoded IDs for @Baggins and @SnazzyDaddy mentions
- **Status Cycle**: Updates every 30 minutes

## How to Run

### Prerequisites
1. Set up the required API keys as environment variables:
   - `DISCORD_BOT_TOKEN`: Get from [Discord Developer Portal](https://discord.com/developers/applications)
   - `LLM_API_KEY`: Get from [Google AI Studio](https://aistudio.google.com/app/apikey)

### Running the Bot
The bot runs automatically via the "Discord Bot" workflow. It will:
1. Validate that API keys are set
2. Connect to Discord
3. Start responding to messages and cycling status

### Deployment
The bot is configured for **Reserved VM (Background Worker)** deployment:
- **Deployment Type**: VM (always-on background worker)
- **Run Command**: `python main.py`
- This configuration is appropriate for Discord bots that need to maintain persistent connections

## User Preferences
None documented yet.

## Security Notes
- API keys are stored as environment variables, not in code
- .gitignore configured to prevent committing sensitive files
- Bot tokens should never be shared or committed to version control

## Future Improvements
- Consider making REPLY_CHANCE configurable via environment variable
- Add more sophisticated conversation history management
- Implement rate limiting for API calls
- Add command handling for bot configuration
