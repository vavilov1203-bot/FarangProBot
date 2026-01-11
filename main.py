import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters


# ===== КНОПКИ (тексты должны совпадать 1-в-1) =====
BTN_RENT = "🏠 Аренда"
BTN_VISAS = "🧾 Визы"
BTN_EXCHANGE = "💱 Обмен валют"
BTN_PHOTO = "📸 Фото и видео"
BTN_TOURS = "🌴 Туры и экскурсии"
BTN_INSURANCE = "🛡️ Страховки"
BTN_CULTURE = "⚠️ Поведение и культура"

BTN_BACK_MAIN = "⬅️ Назад в меню"


# ===== ГЛАВНОЕ МЕНЮ =====
main_menu = [
    [BTN_RENT, BTN_VISAS],
    [BTN_EXCHANGE, BTN_PHOTO],
    [BTN_TOURS, BTN_INSURANCE],
    [BTN_CULTURE],
]

# ===== ПОДМЕНЮ: АРЕНДА =====
rental_menu = [
    ["🏢 Кондо", "🏡 Дома"],
    ["🚗 Автомобили", "🛵 Мотоциклы и байки"],
    [BTN_BACK_MAIN],
]

# ===== ПОДМЕНЮ: ПОВЕДЕНИЕ И КУЛЬТУРА =====
culture_menu = [
    ["🧠 Прежде чем ты начнёшь", "🙏 Тайская культура и табу"],
    ["🙂 Типичные ошибки фарангов", "💡 Как вызывать уважение"],
    ["🧘‍♂️ Сабай-сабай — философия спокойствия"],
    [BTN_BACK_MAIN],
]


def kb(layout):
    return ReplyKeyboardMarkup(layout, resize_keyboard=True)


async def send_main_menu(update: Update, text: str = "Главное меню:"):
    await update.message.reply_text(text, reply_markup=kb(main_menu))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет 👋 Я FarangProBot!\nВыбери нужный раздел:",
        reply_markup=kb(main_menu),
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()

    # --- Назад в главное меню ---
    if text == BTN_BACK_MAIN:
        await send_main_menu(update)
        return

    # --- Главное меню ---
    if text == BTN_RENT:
        await update.message.reply_text("Выбери категорию аренды:", reply_markup=kb(rental_menu))
        return

    if text == BTN_VISAS:
        await update.message.reply_text("🧾 Доступны визы: ED, DTV, Семейная, Бизнес, Пенсионная, Элит и продления штампов.")
        return

    if text == BTN_EXCHANGE:
        await update.message.reply_text("💱 Курсы валют обновляются ежедневно. Напиши, какую валюту хочешь обменять.")
        return

    if text == BTN_PHOTO:
        await update.message.reply_text("📸 Фото- и видеосъёмка мероприятий, недвижимости и бизнеса. Напиши задачу!")
        return

    if text == BTN_TOURS:
        await update.message.reply_text("🌴 Экскурсии по Таиланду: острова, сафари, шоу, храмы — всё под ключ.")
        return

    if text == BTN_INSURANCE:
        await update.message.reply_text("🛡️ Поможем с медицинской страховкой для виз и путешествий.")
        return

    if text == BTN_CULTURE:
        await update.message.reply_text("Выбери тему 👇", reply_markup=kb(culture_menu))
        return

    # --- Подменю “Аренда” (пока заглушки) ---
    if text == "🏢 Кондо":
        await update.message.reply_text("📍 Подбор кондо по району, бюджету и сроку аренды. Напиши параметры!")
        return

    if text == "🏡 Дома":
        await update.message.reply_text("🏡 Найдём дом с садом/бассейном/у моря. Напиши параметры!")
        return

    if text == "🚗 Автомобили":
        await update.message.reply_text("🚗 Аренда авто: автомат/механика, краткосрок/долгосрок. Напиши запрос.")
        return

    if text == "🛵 Мотоциклы и байки":
        await update.message.reply_text("🛵 Байки на день/неделю/месяц. Напиши модель или объём двигателя.")
        return

    # --- Подменю “Поведение и культура” (заглушки) ---
    if text == "🧠 Прежде чем ты начнёшь":
        await update.message.reply_text("Заглушка: позже добавим статью «Прежде чем ты начнёшь».")
        return

    if text == "🙏 Тайская культура и табу":
        await update.message.reply_text("Заглушка: позже добавим правила/табу/поведение в храме и т.д.")
        return

    if text == "🙂 Типичные ошибки фарангов":
        await update.message.reply_text("Заглушка: позже добавим типичные ошибки (агрессия, «я заплатил», и т.д.).")
        return

    if text == "💡 Как вызывать уважение":
        await update.message.reply_text("Заглушка: позже добавим принципы общения и уважения.")
        return

    if text == "🧘‍♂️ Сабай-сабай — философия спокойствия":
        await update.message.reply_text("Заглушка: позже добавим объяснение «сабай-сабай» и как жить проще.")
        return

    # --- Если ввели что-то не из меню ---
    await update.message.reply_text("Выбери пункт из меню 👇", reply_markup=kb(main_menu))


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
