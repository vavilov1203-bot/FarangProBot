import os
from typing import Dict, Any, List

from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ContextTypes, filters
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def content_path(relative_path: str) -> str:
    return os.path.join(BASE_DIR, "content", relative_path)


def load_content(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return "Контент пока не добавлен."


# =========================
# НАСТРОЙКИ КНОПОК
# =========================
BTN_BACK = "⬅️ Назад"
BTN_HOME = "🏠 Главное меню"

# =========================
# ДЕРЕВО МЕНЮ (MVP v1.0)
# =========================
# Формат узла:
# {
#   "_text": "Текст при входе",
#   "_children": {...},
#   "_enabled": True/False (опционально) — скрыть кнопку
# }
#
# Ссылки:
# { "_goto": ["Путь", "до", "узла"] }
MENU_TREE: Dict[str, Any] = {
    "_text": "Выбери пункт из меню 👇",
    "_children": {
        # ==========================================================
        # 🧭 МОЯ СИТУАЦИЯ — главный вход (то, что делает “систему”)
        # ==========================================================
        "🧭 Моя ситуация / С чего начать": {
            "_text": (
                "Выбери ситуацию — и я покажу, с чего начать.\n"
                "Я веду тебя по уже готовым разделам бота 👇"
            ),
            "_children": {
                "🧳 Я только приехал": {
                    "_text": (
                        "Если ты недавно в Таиланде, начни с этого порядка:\n\n"
                        "1️⃣ 💱 Обмен денег\n"
                        "2️⃣ 🧰 Быт и сервисы\n"
                        "3️⃣ 📄 Визовый статус\n"
                        "4️⃣ 🛡️ Страховка / медицина\n"
                        "5️⃣ ⚠️ Поведение и культура\n\n"
                        "Нажимай нужный пункт 👇"
                    ),
                    "_children": {
                        "💱 Обмен валют": {"_goto": ["💱 Обмен валют"]},
                        "🧰 Советы по быту и сервисы": {"_goto": ["🧰 Советы по быту и сервисы"]},
                        "📄 Визы": {"_goto": ["📄 Визы"]},
                        "🛡️ Страховки": {"_goto": ["🛡️ Страховки"]},
                        "⚠️ Поведение и культура": {"_goto": ["⚠️ Поведение и культура"]},
                    },
                },

                "👨‍👩‍👧 Я с семьёй / ребёнок": {
                    "_text": (
                        "Семья/ребёнок: что обычно нужно в первую очередь:\n\n"
                        "1️⃣ 📄 Визы (варианты для семьи)\n"
                        "2️⃣ 🛡️ Страховка (чтобы не платить всё из кармана)\n"
                        "3️⃣ 🧰 Быт/сервисы (школы, кружки, медицина)\n"
                        "4️⃣ ⚠️ Культура (чтобы не попасть в неприятности)\n\n"
                        "Нажимай 👇"
                    ),
                    "_children": {
                        "📄 Визы": {"_goto": ["📄 Визы"]},
                        "🛡️ Страховки": {"_goto": ["🛡️ Страховки"]},
                        "🧰 Советы по быту и сервисы": {"_goto": ["🧰 Советы по быту и сервисы"]},
                        "⚠️ Поведение и культура": {"_goto": ["⚠️ Поведение и культура"]},
                    },
                },

                "🧾 Мне нужно легализоваться подешевле": {
                    "_text": (
                        "Если цель — легализация подешевле, обычно начинают с виз и правил.\n\n"
                        "Открой эти разделы 👇"
                    ),
                    "_children": {
                        "📄 Визы": {"_goto": ["📄 Визы"]},
                        "⚠️ Поведение и культура": {"_goto": ["⚠️ Поведение и культура"]},
                        "🧰 Советы по быту и сервисы": {"_goto": ["🧰 Советы по быту и сервисы"]},
                    },
                },

                "🤒 Нужна медицина / страховка / госпиталь": {
                    "_text": (
                        "Если вопрос про здоровье — начни со страховки.\n\n"
                        "Открой 👇"
                    ),
                    "_children": {
                        "🛡️ Страховки": {"_goto": ["🛡️ Страховки"]},
                    },
                },
            },
        },

        # ==========================================================
        # 📄 ВИЗЫ (пока заглушки — наполнишь позже)
        # ==========================================================
        "📄 Визы": {
            "_text": "Раздел про визы (пока структура/заглушки).",
            "_children": {
                "ED (учебная)": {"_text": "ED-виза — позже заполним.", "_children": {}},
                "DTV (Digital Nomad)": {"_text": "DTV — позже заполним.", "_children": {}},
                "Семейная": {"_text": "Семейная — позже заполним.", "_children": {}},
                "Бизнес": {"_text": "Бизнес — позже заполним.", "_children": {}},
                "Пенсионная": {"_text": "Пенсионная — позже заполним.", "_children": {}},
                "Продление штампов": {"_text": "Продления — позже заполним.", "_children": {}},
            },
        },

        # ==========================================================
        # 🛡️ СТРАХОВКИ — уже через content (MVP-контент)
        # ==========================================================
        "🛡️ Страховки": {
            "_text": load_content(content_path("insurance/intro.md")),
            "_children": {
                "{ } Прежде чем выбирать": {
                    "_text": load_content(content_path("insurance/before_choose.md")),
                    "_children": {}
                },
                "💳 Как работает cashless": {
                    "_text": load_content(content_path("insurance/cashless.md")),
                    "_children": {}
                },
                "📉 Франшиза, лимиты, исключения": {
                    "_text": load_content(content_path("insurance/deductible_limits_exclusions.md")),
                    "_children": {}
                },
                "❌ Топ ошибок при покупке": {
                    "_text": load_content(content_path("insurance/common_mistakes.md")),
                    "_children": {}
                },
                "✅ Где покупать и как проверять": {
                    "_text": load_content(content_path("insurance/where_to_buy_and_check.md")),
                    "_children": {}
                },
            },
        },

        # ==========================================================
        # 💱 ОБМЕН ВАЛЮТ (пока заглушки)
        # ==========================================================
        "💱 Обмен валют": {
            "_text": "Обмен валют — курсы, где менять, безопасность (пока структура).",
            "_children": {
                "Где выгоднее менять": {"_text": "Позже добавим гайд и примеры.", "_children": {}},
                "Безопасность": {"_text": "Позже добавим чек-лист.", "_children": {}},
                "Крипта": {"_text": "Позже добавим аккуратный раздел.", "_children": {}},
            },
        },

        # ==========================================================
        # ⚠️ ПОВЕДЕНИЕ И КУЛЬТУРА (у тебя уже через content частично)
        # ==========================================================
        "⚠️ Поведение и культура": {
            "_text": "Поведение и культура — что важно знать в Таиланде.",
            "_children": {
                "{ } Прежде чем ты начнёшь": {
                    "_text": load_content(content_path("behavior/before_you_start.md")),
                    "_children": {},
                },

                "🙏 Тайская культура и табу": {
                    "_text": load_content(content_path("taboo/intro.md")),
                    "_children": {
                        "👑 Король, религия и «святые» темы": {
                            "_text": load_content(content_path("taboo/king_religion.md")),
                            "_children": {},
                        },
                        "⛩️ Как вести себя в храме": {
                            "_text": load_content(content_path("taboo/temple_rules.md")),
                            "_children": {},
                        },
                        "👣 Голова, ноги, касания": {
                            "_text": load_content(content_path("taboo/head_feet_touch.md")),
                            "_children": {},
                        },
                        "👕 Одежда и нормы": {
                            "_text": load_content(content_path("taboo/clothes_public_norms.md")),
                            "_children": {},
                        },
                    },
                },

                "🙂 Типичные ошибки фарангов": {
                    "_text": load_content(content_path("mistakes/intro.md")),
                    "_children": {
                        "💸 Я заплатил — значит, можно": {
                            "_text": load_content(content_path("mistakes/i_paid_so_i_can.md")),
                            "_children": {},
                        },
                        "😡 Агрессия и алкоголь": {
                            "_text": load_content(content_path("mistakes/aggression_alcohol.md")),
                            "_children": {},
                        },
                        "🍻 Тайки, бары и чувство меры": {
                            "_text": load_content(content_path("mistakes/bars_and_boundaries.md")),
                            "_children": {},
                        },
                        "🏍 Нелегальная работа, мотоциклы без прав": {
                            "_text": load_content(content_path("mistakes/illegal_work_and_bike.md")),
                            "_children": {},
                        },
                    },
                },

                "💡 Как вызывать уважение": {
                    "_text": load_content(content_path("respect/intro.md")),
                    "_children": {
                        "Вежливость — не слабость": {
                            "_text": load_content(content_path("respect/politeness_not_weakness.md")),
                            "_children": {},
                        },
                        "Сохранять лицо даже в споре": {
                            "_text": load_content(content_path("respect/save_face_in_conflict.md")),
                            "_children": {},
                        },
                        "Слушать, а не доказывать": {
                            "_text": load_content(content_path("respect/listen_dont_prove.md")),
                            "_children": {},
                        },
                        "Простые фразы, которые помогают": {
                            "_text": load_content(content_path("respect/helpful_phrases.md")),
                            "_children": {},
                        },
                    },
                },

                "🧘‍♂️ Сабай-сабай": {
                    "_text": load_content(content_path("sabai/intro.md")),
                    "_children": {
                        "Что значит “сабай” и “санук”": {
                            "_text": load_content(content_path("sabai/sabai_sanuk.md")),
                            "_children": {}
                        },
                        "Почему тайцы не спешат": {
                            "_text": load_content(content_path("sabai/why_not_hurry.md")),
                            "_children": {}
                        },
                        "Как жить в хаосе": {
                            "_text": load_content(content_path("sabai/live_with_chaos.md")),
                            "_children": {}
                        },
                        "Внутренний баланс": {
                            "_text": load_content(content_path("sabai/inner_balance.md")),
                            "_children": {}
                        },
                    }
                },
            },
        },

        # ==========================================================
        # 🧰 БЫТ И СЕРВИСЫ (пока заглушка)
        # ==========================================================
        "🧰 Советы по быту и сервисы": {
            "_text": "Быт и сервисы — пока в разработке. Скоро будет много полезного.",
            "_children": {},
        },

        # ==========================================================
        # ВСЁ ОСТАЛЬНОЕ — СКРЫТО В MVP (чтобы бот был “собранным”)
        # ==========================================================
        "🏠 Аренда": {
            "_enabled": False,
            "_text": "Аренда — временно скрыто в MVP.",
            "_children": {},
        },
        "📸 Фото и видео": {
            "_enabled": False,
            "_text": "Фото/видео — временно скрыто в MVP.",
            "_children": {},
        },
        "🌴 Туры и экскурсии": {
            "_enabled": False,
            "_text": "Туры — временно скрыто в MVP.",
            "_children": {},
        },
        "🐾 Животные и переезд": {
            "_enabled": False,
            "_text": "Животные — временно скрыто в MVP.",
            "_children": {},
        },
        "💼 Работа и налоги": {
            "_enabled": False,
            "_text": "Работа/налоги — временно скрыто в MVP.",
            "_children": {},
        },
    },
}


# =========================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =========================
def get_node_by_path(path: List[str]) -> Dict[str, Any]:
    node = MENU_TREE
    for step in path:
        node = node["_children"][step]
    return node


def make_keyboard(node: Dict[str, Any], is_root: bool) -> ReplyKeyboardMarkup:
    children = node.get("_children", {})

    # ✅ показываем только включённые пункты (если _enabled нет — считаем True)
    buttons = [
        k for k, v in children.items()
        if isinstance(v, dict) and v.get("_enabled", True)
    ]

    rows = [[b] for b in buttons]  # по 1 кнопке в строке

    if not is_root:
        rows.append([BTN_BACK, BTN_HOME])

    return ReplyKeyboardMarkup(rows, resize_keyboard=True)


async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    path: List[str] = context.user_data.get("path", [])
    node = get_node_by_path(path) if path else MENU_TREE

    text = node.get("_text", "Выбери пункт из меню 👇")
    kb = make_keyboard(node, is_root=(len(path) == 0))

    await update.message.reply_text(
        text,
        reply_markup=kb,
        parse_mode=None,
        disable_web_page_preview=True
    )


# =========================
# ХЭНДЛЕРЫ
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["path"] = []
    await show_menu(update, context)


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    txt = (update.message.text or "").strip()
    path: List[str] = context.user_data.get("path", [])

    if txt == BTN_HOME:
        context.user_data["path"] = []
        await show_menu(update, context)
        return

    if txt == BTN_BACK:
        if path:
            path.pop()
        context.user_data["path"] = path
        await show_menu(update, context)
        return

    node = get_node_by_path(path) if path else MENU_TREE
    children = node.get("_children", {})

    # ✅ не даём входить в выключенные пункты
    if txt in children and isinstance(children[txt], dict) and children[txt].get("_enabled", True):
        next_node = children[txt]

        # ✅ поддержка "_goto"
        if "_goto" in next_node:
            context.user_data["path"] = list(next_node["_goto"])
        else:
            path.append(txt)
            context.user_data["path"] = path

        await show_menu(update, context)
        return

    await update.message.reply_text("Выбери пункт кнопкой 👇")


def main() -> None:
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("Не найден BOT_TOKEN в переменных окружения")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
