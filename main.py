import os
import logging
from openai import OpenAI
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# === СЕКРЕТЫ ЧЕРЕЗ ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ ===
# (на Render ты их задашь в настройках сервиса)
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = (
    "Ты — Farang Pro, дружелюбный и честный помощник по Таиланду, Аргентине и релокации. "
    "Отвечай кратко, по делу, простым языком. Если спрашивают про законы/процедуры, давай пошагово."
)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("farangpro")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name or "друг"
    await update.message.reply_text(
        f"Привет, {name}! Я Farang Pro. Спроси меня что угодно про Таиланд/Аргентину, визы, жильё, деньги, перелёты и т.д."
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Напиши вопрос одним сообщением. Я постараюсь ответить максимально конкретно.\n"
        "Команды: /start, /help"
    )

def ask_openai(prompt_text: str) -> str:
    # Chat Completions (универсально и дёшево)
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt_text},
        ],
        temperature=0.3,
    )
    return resp.choices[0].message.content.strip()

async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    if not text:
        return
    chat_id = update.effective_chat.id
    user = update.effective_user

    log.info("Q from %s (%s): %s", user.id, user.first_name, text)

    try:
        reply = ask_openai(text)
    except Exception as e:
        log.exception("OpenAI error: %s", e)
        reply = "Упс, у меня сейчас перегрузка. Попробуй повторить сообщение ещё раз через минуту."

    await update.message.reply_text(reply, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))

    log.info("Bot started. Polling…")
    app.run_polling(close_loop=False)

if __name__ == "__main__":
    main()
