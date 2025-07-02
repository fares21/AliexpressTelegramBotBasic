# AliExpress Telegram Bot

A Telegram bot that helps users find AliExpress products and affiliate links. This bot provides product searches, affiliate link generation, and automated posting features.

## Features

- 🔍 Product search on AliExpress
- 🔗 Affiliate link generation
- 📱 Telegram bot interface
- 🛒 Shopping cart functionality
- 📊 Product details and pricing

## Setup

### Prerequisites

- Python 3.7+
- Telegram Bot Token (from @BotFather)
- AliExpress API credentials

### Installation

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd AliexpressBot_Github
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Then edit .env with your actual API keys and tokens
   ```

   Or set environment variables manually:
   ```bash
   # Windows (Command Prompt)
   set TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   set ALIEXPRESS_API_PUBLIC=your_aliexpress_api_public_key
   set ALIEXPRESS_API_SECRET=your_aliexpress_api_secret_key
   
   # Windows (PowerShell)
   $env:TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
   $env:ALIEXPRESS_API_PUBLIC="your_aliexpress_api_public_key"
   $env:ALIEXPRESS_API_SECRET="your_aliexpress_api_secret_key"
   
   # Linux/Mac
   export TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
   export ALIEXPRESS_API_PUBLIC="your_aliexpress_api_public_key"
   export ALIEXPRESS_API_SECRET="your_aliexpress_api_secret_key"
   ```

### Usage

1. **For Development (Local Testing):**
   ```bash
   python Bot.py
   ```
   This will start the bot in polling mode, perfect for local development and testing.

2. **For Production (Webhook Mode):**
   Set the `WEBHOOK_URL` environment variable:
   ```bash
   export WEBHOOK_URL="https://your-domain.com/webhook"
   python Bot.py
   ```

## How to Get API Credentials

### Telegram Bot Token
1. Go to [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow the instructions
3. Copy the bot token provided

### AliExpress API Credentials
1. Go to [AliExpress Open Platform](https://open.aliexpress.com/)
2. Sign up/login to your account
3. Create a new application
4. Get your `App Key` (API Public) and `App Secret` (API Secret)

## Files Description

- `Bot.py` - Main bot implementation with Flask webhook
- `set_webhook.py` - Webhook configuration script
- `aliexpress_api/` - Custom AliExpress API wrapper
- `.env.example` - Environment variables template

## Environment Variables

Make sure to set these environment variables before running the bot:

- `TELEGRAM_BOT_TOKEN` - Your Telegram bot token
- `ALIEXPRESS_API_PUBLIC` - Your AliExpress API public key
- `ALIEXPRESS_API_SECRET` - Your AliExpress API secret key

## Contributing

Feel free to fork this project and submit pull requests for any improvements.

## License

This project is open source and available under the MIT License.