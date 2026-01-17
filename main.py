import os
from typing import Dict, Any, List

from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ContextTypes, filters
)

# =========================
# BASE
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def content_path(relative_path: str) -> str:
    return os.path.join(BASE_DIR, "content", relative_path)


def load_content(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return f"Контент пока не добавлен.\n\n(Файл не найден: {path})"


# =========================
# КНОПКИ
# =========================
BTN_BACK = "⬅️ Назад"
BTN_HOME = "🏠 Главное меню"

# =========================
# MENU TREE (V1)
# =========================
MENU_TREE: Dict[str, Any] = {
    "_text": "Выбери пункт из меню 👇",
    "_children": {

        # ==================================================
        # 🧭 МОЯ СИТУАЦИЯ — ГЛАВНЫЙ ВХОД
        # ==================================================
        "🧭 Моя ситуация / С чего начать": {
            "_text": load_content(content_path("situations/intro.md")),
            "_children": {

                # -------------------------
                # 🧳 Я только приехал
                # -------------------------
                "🧳 Я только приехал": {
                    "_text": load_content(content_path("situations/just_arrived.md")),
                    "_children": {
                        "💱 Обмен денег — как сделать правильно": {
                            "_text": load_content(content_path("situations/just_arrived_exchange.md")),
                            "_children": {
                                "➡️ Перейти к разделу: 💱 Обмен валют": {
                                    "_goto": ["💱 Обмен валют"]
                                }
                            }
                        },
                        "🧰 Быт и сервисы — что поставить в первый день": {
                            "_text": load_content(content_path("situations/just_arrived_services.md")),
                            "_children": {
                                "➡️ Перейти к разделу: 🧰 Советы по быту и сервисы": {
                                    "_goto": ["🧰 Советы по быту и сервисы"]
                                }
                            }
                        },
                        "📄 Визовый статус — как понять, что у тебя сейчас": {
                            "_text": load_content(content_path("situations/just_arrived_visa_status.md")),
                            "_children": {
                                "➡️ Перейти к разделу: 📄 Визы": {
                                    "_goto": ["📄 Визы"]
                                }
                            }
                        },
                        "🛡️ Страховка/медицина — что делать первым делом": {
                            "_text": load_content(content_path("situations/just_arrived_insurance.md")),
                            "_children": {
                                "➡️ Перейти к разделу: 🛡️ Страховки": {
                                    "_goto": ["🛡️ Страховки"]
                                }
                            }
                        },
                        "⚠️ Культура — что нельзя делать точно": {
                            "_text": load_content(content_path("situations/just_arrived_culture.md")),
                            "_children": {
                                "➡️ Перейти к разделу: ⚠️ Поведение и культура": {
                                    "_goto": ["⚠️ Поведение и культура"]
                                }
                            }
                        },
                    }
                },

                # -------------------------
                # 👨‍👩‍👦 Я с семьёй / ребёнок
                # -------------------------
                "👨‍👩‍👦 Я с семьёй / ребёнок": {
                    "_text": load_content(content_path("situations/with_family.md")),
                    "_children": {
                        "🏠 Жильё для семьи — как выбирать": {
                            "_text": load_content(content_path("situations/family_rent.md")),
                            "_children": {}
                        },

                        "📄 Визы для семьи": {
                            "_disabled": True,  # V2
                            "_text": load_content(content_path("situations/family_visas.md")),
                            "_children": {}
                        },

                        "🛡️ Страховка для семьи": {
                            "_disabled": True,  # V2
                            "_text": load_content(content_path("situations/family_insurance.md")),
                            "_children": {}
                        },

                        "🧰 Быт с ребёнком": {
                            "_text": load_content(content_path("situations/family_services.md")),
                            "_children": {}
                        },

                        "⚠️ Культура и школа": {
                            "_disabled": True,  # V2
                            "_text": load_content(content_path("situations/family_culture.md")),
                            "_children": {}
                        },
                    }
                },
            }
        },

        # ==================================================
        # ОСНОВНЫЕ РАЗДЕЛЫ (V1)
        # ==================================================
        "📄 Визы": {
            "_text": "Раздел про визы и легализацию.",
            "_children": {}
        },

        "🛡️ Страховки": {
            "_text": "Медицина и страховки.",
            "_children": {}
        },

        "⚠️ Поведение и культура": {
            "_text": load_content(content_path("behavior/before_you_start.md")),
            "_children": {}
        },

        "🧰 Советы по быту и сервисы": {
            "_text": "Бытовой хаб. Будем наполнять.",
            "_children": {}
        },

        # ==================================================
        # ОСТАЛЬНЫЕ РАЗДЕЛЫ (V2 — просто лежат)
        # ==================================================
        "💱 Обмен валют": {"_disabled": True, "_text": "V2", "_children": {}},
        "🏠 Аренда": {"_disabled": True, "_text": "V2", "_children": {}},
        "📸 Фото и видео": {"_disabled": True, "_text": "V2", "_children": {}},
        "🌴 Туры и экскурсии": {"_disabled": True, "_text": "V2", "_children": {}},
        "💼 Работа и налоги": {"_disabled": True, "_text": "V2", "_children": {}},
    }
}

# =========================
# FILTER DISABLED
# =========================
def prune_disabled(node: Dict[str, Any]) -> Dict[str, Any]:
    children = node.get("_children", {})
    if not isinstance(children, dict):
        return node

    new_children = {}
    for k, v in children.items():
        if isinstance(v, dict) and v.get("_disabled"):
            continue
        new_children[k] = prune_disabled(v) if isinstance(v, dict) else v

    node["_children"] = new_children
    return node


MENU_TREE = prune_disabled(MENU_TREE)

# =========================
# HELPERS
# =========================
def get_node_by_path(path: List[str]) -> Dict[str, Any]:
    node = MENU_TREE
    for step in path:
        node = node["_children"][step]
    return node


def make_keyboard(node: Dict[str, Any], is_root: bool) -> ReplyKeyboardMarkup:
    rows = [[k] for k in node.get("_children", {}).keys()]
    if not is_root:
        rows.append([BTN_BACK, BTN_HOME])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)


async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    path = context.user_data.get("path", [])
    node = get_node_by_path(path) if path else MENU_TREE
    await update.message.reply_text(
        node.get("_text", "Выбери пункт 👇"),
        reply_markup=make_keyboard(node, is_root=not path),
        disable_web_page_preview=True
    )

# =========================
# HANDLERS
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["path"] = []
    await show_menu(update, context)


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text.strip()
    path = context.user_data.get("path", [])

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

    if txt in children:
        next_node = children[txt]
        if "_goto" in next_node:
            context.user_data["path"] = list(next_node["_goto"])
        else:
            path.append(txt)
            context.user_data["path"] = path
        await show_menu(update, context)
        return

    await update.message.reply_text("Пожалуйста, используй кнопки 👇")

# =========================
# MAIN
# =========================
def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN не найден")

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
    app.run_polling()


if __name__ == "__main__":
    main()
