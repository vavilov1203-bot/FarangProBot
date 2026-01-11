import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Главное меню
main_menu = [
    ["🏠 Аренда", "🪪 Визы"],
    ["💱 Обмен валюты", "📸 Фото и видео"],
    ["🌴 Туры и экскурсии", "🏥 Страховки"]
    ["⚠️ Поведение и культура"]
]

# Подменю аренды
rental_menu = [
    ["🏢 Кондо", "🏡 Дома"],
    ["🚗 Автомобили", "🛵 Мотоциклы и байки"],
    ["⬅️ Назад в меню"]
]
# Подменю "Поведение и культура"
culture_menu = [
    ["🧩 Прежде чем ты начнёшь", "🙏 Тайская культура и табу"],
    ["🙂 Типичные ошибки фарангов", "💡 Как вызывать уважение"],
    ["🧘 Сабай-сабай — философия спокойствия"],
    ["⬅️ Назад в меню"]
]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = ReplyKeyboardMarkup(main_menu, resize_keyboard=True)
    await update.message.reply_text(
        "Привет 👋 Я FarangProBot! Помогу с жизнью в Таиланде 🇹🇭\nВыбери нужный раздел:",
        reply_markup=reply_markup
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # --- Главное меню ---
    if text == "🏠 Аренда":
        reply_markup = ReplyKeyboardMarkup(rental_menu, resize_keyboard=True)
        await update.message.reply_text("Выбери категорию аренды:", reply_markup=reply_markup)

    elif text == "🪪 Визы":
        await update.message.reply_text("📄 Доступны визы: ED, DTV, Семейная, Бизнес, Пенсионная, Элит и продления штампов.")

    elif text == "💱 Обмен валюты":
        await update.message.reply_text("💰 Курсы валют обновляются ежедневно. Напиши, какую валюту хочешь обменять.")

    elif text == "📸 Фото и видео":
        await update.message.reply_text("📷 Фото- и видеосъёмка мероприятий, недвижимости и бизнеса. Напиши задачу!")

    elif text == "🌴 Туры и экскурсии":
        await update.message.reply_text("🏖️ Экскурсии по Таиланду: острова, сафари, шоу, храмы — всё под ключ.")

    elif text == "🏥 Страховки":
        await update.message.reply_text("🩺 Поможем с медицинской страховкой для виз и путешествий.")
    
    elif text == "⚠️ Поведение и культура":
    reply_markup = ReplyKeyboardMarkup(culture_menu, resize_keyboard=True)
        await update.message.reply_text("Выбери тему:", reply_markup=reply_markup)

    # --- Подменю аренды ---
    elif text == "🏢 Кондо":
        await update.message.reply_text("📍 Подбор кондо по району, бюджету и сроку аренды. Напиши параметры!")

    elif text == "🏡 Дома":
        await update.message.reply_text("🏡 Найдём дом с садом, бассейном или у моря. Укажи, что ищешь.")

    elif text == "🚗 Автомобили":
        await update.message.reply_text("🚘 Аренда авто с автоматом/механикой, долгосрочно и краткосрочно.")

    elif text == "🛵 Мотоциклы и байки":
        await update.message.reply_text("🛵 Есть байки на день, неделю или месяц. Укажи модель или объём двигателя.")
    
    # --- Подменю "Поведение и культура" ---
    elif text == "🧩 Прежде чем ты начнёшь":
        await update.message.reply_text("Заглушка: сюда позже добавим текст/статью по теме «Прежде чем ты начнёшь».")

    elif text == "🙏 Тайская культура и табу":
        await update.message.reply_text("Заглушка: сюда позже добавим правила/табу/поведение в храме и т.д.")

    elif text == "🙂 Типичные ошибки фарангов":
        await update.message.reply_text("Заглушка: сюда позже добавим типичные ошибки (агрессия, «я заплатил», и т.п.).")

    elif text == "💡 Как вызывать уважение":
        await update.message.reply_text("Заглушка: сюда позже добавим принципы общения и уважения.")

    elif text == "🧘 Сабай-сабай — философия спокойствия":
        await update.message.reply_text("Заглушка: сюда позже добавим объяснение «сабай-сабай» и как жить проще.")

    elif text == "⬅️ Назад в меню":
        reply_markup = ReplyKeyboardMarkup(main_menu, resize_keyboard=True)
        await update.message.reply_text("Главное меню:", reply_markup=reply_markup)

    # --- Остальное ---
    else:
        await update.message.reply_text("Выбери пункт из меню 👇")


def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("❌ Ошибка: не найден TELEGRAM_BOT_TOKEN")
        return

    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()


if __name__ == "__main__":
    main()
