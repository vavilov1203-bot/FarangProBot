import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Логи (чтобы видеть ошибки в Render)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! 👋 Бот успешно работает на Render!")

# Основная функция запуска
def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("❌ Ошибка: отсутствует TELEGRAM_BOT_TOKEN")
        return

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))

    print("✅ Бот запущен и ждёт сообщений...")
    app.run_polling()

if __name__ == "__main__":
    main()
