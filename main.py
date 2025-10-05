import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

client = OpenAI(api_key=OPENAI_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я FarangProBot — твой помощник по Таиланду 🇹🇭")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Пока я учусь, но скоро смогу помогать с визами, жильём и бизнесом в Таиланде!")

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    app.run_polling()

if __name__ == "__main__":
    main()