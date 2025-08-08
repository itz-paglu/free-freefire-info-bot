import os
import telebot
import requests
import threading
import sys
import logging
from flask import Flask
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes, AIORateLimiter
)
import asyncio
from dotenv import load_dotenv
from cogs.infoCommands import info_command  # Custom command handler

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("Missing TOKEN in environment")

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Flask setup for health check
app = Flask(__name__)
bot_name = "Loading..."

@app.route('/')
def home():
    return f"Bot {bot_name} is operational"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# Telegram command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I’m alive.")

# Background task (e.g., periodic message to admin or logging)
async def periodic_task(app):
    while True:
        logging.info("✅ Periodic task running...")
        await asyncio.sleep(300)  # 5 minutes

async def main():
    global bot_name

    # Initialize Telegram bot
    application = (
        ApplicationBuilder()
        .token(TOKEN)
        .rate_limiter(AIORateLimiter())
        .build()
    )

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("info", info_command))

    # Set bot_name
    me = await application.bot.get_me()
    bot_name = me.username
    logging.info(f"🔗 Connected as @{bot_name}")

    # Start Flask if on Render
    if os.environ.get("RENDER"):
        import threading
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        logging.info("🚀 Flask server started")

    # Start background task
    application.job_queue.run_repeating(
        lambda ctx: logging.info("⏱️ Status update placeholder"), interval=300
    )

    # Start bot
    await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
