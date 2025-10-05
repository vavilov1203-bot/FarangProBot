import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ FarangProBot запущен и готов работать!")

def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("❌ Ошибка: не найден TELEGRAM_BOT_TOKEN")
        return

    # Создаём приложение
    app = ApplicationBuilder().token(token).build()

    # Добавляем команду /start
    app.add_handler(CommandHandler("start", start))

    # Запускаем поллинг
    app.run_polling()

if __name__ == "__main__":
    main()
