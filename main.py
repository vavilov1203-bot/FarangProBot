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
        return f"Контент пока не добавлен.\n\n(Файл не найден: {path})"


# =========================
# НАСТРОЙКИ КНОПОК
# =========================
BTN_BACK = "⬅️ Назад"
BTN_HOME = "🏠 Главное меню"

# =========================
# УДОБНОЕ ОТКЛЮЧЕНИЕ РАЗДЕЛОВ
# =========================
# Можно отключить любой узел, добавив в него:
# "_disabled": True
#
# Пример:
# "📸 Фото и видео": { "_disabled": True, "_text": "...", "_children": {...} }
#
# Или можешь отключать по точному названию кнопки из root:
DISABLED_ROOT_BUTTONS = set([
    # тут ничего не нужно, мы просто НЕ добавляем лишние кнопки в root
])

# =========================
# ДЕРЕВО МЕНЮ (СТРУКТУРА)
# =========================
MENU_TREE: Dict[str, Any] = {
    "_text": "Выбери пункт из меню 👇",
    "_children": {
        # ==========================================================
        # ✅ 1) 🧭 МОЯ СИТУАЦИЯ / С ЧЕГО НАЧАТЬ (с 2-м уровнем)
        # ==========================================================
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
                                "➡️ Открыть основной раздел: 💱 Обмен валют": {
                                    "_goto": ["🧭 Моя ситуация / С чего начать", "💱 Обмен валют"]
                                },
                            },
                        },
                        "🧰 Быт и сервисы — что поставить в первый день": {
                            "_text": load_content(content_path("situations/just_arrived_services.md")),
                            "_children": {
                                "➡️ Открыть основной раздел: 🧰 Советы по быту и сервисы": {"_goto": ["🧰 Советы по быту и сервисы"]},
                            },
                        },
                        "📄 Визовый статус — как понять, что у тебя сейчас": {
                            "_text": load_content(content_path("situations/just_arrived_visa_status.md")),
                            "_children": {
                                "➡️ Открыть основной раздел: 📄 Визы": {"_goto": ["📄 Визы"]},
                            },
                        },
                        "🛡️ Страховка/медицина — что делать первым делом": {
                            "_text": load_content(content_path("situations/just_arrived_insurance.md")),
                            "_children": {
                                "➡️ Открыть основной раздел: 🛡️ Страховки": {"_goto": ["🛡️ Страховки"]},
                            },
                        },
                        "⚠️ Культура — что нельзя делать точно": {
                            "_text": load_content(content_path("situations/just_arrived_culture.md")),
                            "_children": {
                                "➡️ Открыть основной раздел: ⚠️ Поведение и культура": {"_goto": ["⚠️ Поведение и культура"]},
                            },
                        },
                    },
                },

                # -------------------------
                # 👨‍👩‍👦 Я с семьёй / ребёнок
                # -------------------------
                "👨‍👩‍👦 Я с семьёй / ребёнок": {
                    "_text": load_content(content_path("situations/with_family.md")),
                    "_children": {
                        "🏠 Жильё для семьи — как выбирать": {
                            "_text": load_content(content_path("situations/family_rent.md")),
                            "_children": {
                                "➡️ Открыть основной раздел: 🧰 Советы по быту и сервисы": {"_goto": ["🧰 Советы по быту и сервисы"]},
                            },
                        },
                        "📄 Визы для семьи — что реально тянется по деньгам": {
                            "_text": load_content(content_path("situations/family_visas.md")),
                            "_children": {
                                "➡️ Открыть основной раздел: 📄 Визы": {"_goto": ["📄 Визы"]},
                            },
                        },
                        "🛡️ Страховка для семьи — как не разориться на медицине": {
                            "_text": load_content(content_path("situations/family_insurance.md")),
                            "_children": {
                                "➡️ Открыть основной раздел: 🛡️ Страховки": {"_goto": ["🛡️ Страховки"]},
                            },
                        },
                        "🧰 Быт с ребёнком — транспорт/сервисы": {
                            "_text": load_content(content_path("situations/family_services.md")),
                            "_children": {
                                "➡️ Открыть основной раздел: 🧰 Советы по быту и сервисы": {"_goto": ["🧰 Советы по быту и сервисы"]},
                            },
                        },
                        "⚠️ Культура — чтобы не было проблем у семьи": {
                            "_text": load_content(content_path("situations/family_culture.md")),
                            "_children": {
                                "➡️ Открыть основной раздел: ⚠️ Поведение и культура": {"_goto": ["⚠️ Поведение и культура"]},
                            },
                        },
                    },
                },

                # -------------------------
                # 📄 Мне нужно легализоваться подешевле
                # -------------------------
                "📄 Мне нужно легализоваться подешевле": {
                    "_text": load_content(content_path("situations/cheap_legalization.md")),
                    "_children": {
                        "🧾 Шаг 1 — понять статус и сроки": {
                            "_text": load_content(content_path("situations/cheap_step1_status.md")),
                            "_children": {
                                "➡️ Открыть основной раздел: 📄 Визы": {"_goto": ["📄 Визы"]},
                            },
                        },
                        "💸 Шаг 2 — выбрать самый дешевый безопасный вариант": {
                            "_text": load_content(content_path("situations/cheap_step2_options.md")),
                            "_children": {
                                "➡️ Открыть основной раздел: 📄 Визы": {"_goto": ["📄 Визы"]},
                            },
                        },
                        "⚠️ Красные флаги “помогаторов”": {
                            "_text": load_content(content_path("situations/cheap_red_flags.md")),
                            "_children": {
                                "➡️ Открыть основной раздел: 📄 Визы": {"_goto": ["📄 Визы"]},
                            },
                        },
                    },
                },

                # -------------------------
                # 🧠 Нужна медицина / страховка / госпиталь
                # -------------------------
                "🧠 Нужна медицина / страховка / госпиталь": {
                    "_text": load_content(content_path("situations/medicine_and_insurance.md")),
                    "_children": {
                        "🚑 Срочно или нет — как понять": {
                            "_text": load_content(content_path("situations/med_urgent.md")),
                            "_children": {
                                "➡️ Открыть основной раздел: 🛡️ Страховки": {"_goto": ["🛡️ Страховки"]},
                            },
                        },
                        "🧾 Если есть страховка — как пользоваться правильно": {
                            "_text": load_content(content_path("situations/med_with_insurance.md")),
                            "_children": {
                                "➡️ Открыть основной раздел: 🛡️ Страховки": {"_goto": ["🛡️ Страховки"]},
                            },
                        },
                        "💳 Если страховки нет — как не переплатить": {
                            "_text": load_content(content_path("situations/med_no_insurance.md")),
                            "_children": {
                                "➡️ Открыть основной раздел: 🛡️ Страховки": {"_goto": ["🛡️ Страховки"]},
                            },
                        },
                    },
                },

                # ----------------------------------------------------------
                # ✅ “ОСНОВНОЙ РАЗДЕЛ” ОБМЕНА — ВНУТРИ МОЕЙ СИТУАЦИИ (НЕ ROOT!)
                # ----------------------------------------------------------
                "💱 Обмен валют": {
                    "_text": "Обмен валют — курсы, где менять, безопасность.",
                    "_children": {
                        "Где выгоднее менять": {"_text": "Где выгоднее — банки/обменники/приложения.", "_children": {}},
                        "Безопасность": {"_text": "Как не попасть на подмену/фейки.", "_children": {}},
                        "Крипта": {"_text": "Крипта — легальность и риски (общая инфа).", "_children": {}},
                    },
                },
            },
        },

        # ==========================================================
        # ✅ 2) 📄 ВИЗЫ (с подразделами — вернуть как было)
        # ==========================================================
        "📄 Визы": {
            "_text": "Раздел про визы и легализацию.",
            "_children": {
                "ED (учебная)": {"_text": "ED-виза — структура раздела (позже наполним).", "_children": {}},
                "DTV (Digital Nomad)": {"_text": "DTV — условия, документы, подача.", "_children": {}},
                "Семейная": {"_text": "Семейная виза — варианты и требования.", "_children": {}},
                "Бизнес": {"_text": "Бизнес-виза — как легально работать.", "_children": {}},
                "Пенсионная": {"_text": "Пенсионная — требования и продления.", "_children": {}},
                "Элит": {"_text": "Elite — пакеты, цены, нюансы.", "_children": {}},
                "Продление штампов": {"_text": "Продления — сроки, штрафы, лайфхаки.", "_children": {}},
            },
        },

        # ==========================================================
        # ✅ 3) 🛡️ СТРАХОВКИ
        # ==========================================================
        "🛡️ Страховки": {
            "_text": "Страховки — здоровье, путешествия, авто/байк, имущество.",
            "_children": {
                "Медицинская": {"_text": "Медицинская страховка — как выбрать.", "_children": {}},
                "Путешествия": {"_text": "Travel страховка — нюансы.", "_children": {}},
                "Авто/байк": {"_text": "Авто/байк страховка — что покрывает.", "_children": {}},
            },
        },

        # ==========================================================
        # ✅ 4) ⚠️ ПОВЕДЕНИЕ И КУЛЬТУРА
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
            },
        },

        # ==========================================================
        # ✅ 5) 🧰 СОВЕТЫ ПО БЫТУ И СЕРВИСЫ
        # ==========================================================
        "🧰 Советы по быту и сервисы": {
            "_text": "Бытовой хаб. Будем наполнять.",
            "_children": {},
        },
    },
}


# =========================
# СЛУЖЕБНО: ФИЛЬТР ОТКЛЮЧЕННЫХ УЗЛОВ
# =========================
def is_disabled(name: str, node: Dict[str, Any], is_root: bool) -> bool:
    if isinstance(node, dict) and node.get("_disabled") is True:
        return True
    if is_root and name in DISABLED_ROOT_BUTTONS:
        return True
    return False


def prune_disabled(node: Dict[str, Any], is_root: bool = False) -> Dict[str, Any]:
    children = node.get("_children", {})
    if not isinstance(children, dict):
        return node

    new_children: Dict[str, Any] = {}
    for k, v in children.items():
        if isinstance(v, dict) and is_disabled(k, v, is_root=is_root):
            continue
        if isinstance(v, dict):
            new_children[k] = prune_disabled(v, is_root=False)
        else:
            new_children[k] = v

    node["_children"] = new_children
    return node


# Применяем фильтрацию один раз при старте
MENU_TREE = prune_disabled(MENU_TREE, is_root=True)


# =========================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =========================
def get_node_by_path(path: List[str]) -> Dict[str, Any]:
    node = MENU_TREE
    for step in path:
        node = node["_children"][step]
    return node


def make_keyboard(node: Dict[str, Any], is_root: bool) -> ReplyKeyboardMarkup:
    buttons = list(node.get("_children", {}).keys())

    rows = []
    for b in buttons:
        rows.append([b])  # по 1 кнопке в строке

    # навигация
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

    # HOME
    if txt == BTN_HOME:
        context.user_data["path"] = []
        await show_menu(update, context)
        return

    # BACK
    if txt == BTN_BACK:
        if path:
            path.pop()
        context.user_data["path"] = path
        await show_menu(update, context)
        return

    # переход по дереву
    node = get_node_by_path(path) if path else MENU_TREE
    children = node.get("_children", {})

    if txt in children:
        next_node = children[txt]

        # ✅ поддержка "_goto"
        if isinstance(next_node, dict) and "_goto" in next_node:
            context.user_data["path"] = list(next_node["_goto"])
        else:
            path.append(txt)
            context.user_data["path"] = path

        await show_menu(update, context)
        return

    # если текст не кнопка
    await update.message.reply_text("Пожалуйста, используй кнопки 👇")


def main() -> None:
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("Не найден BOT_TOKEN в переменных окружения")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))

    # ВАЖНО: запускай либо polling, либо webhook (НЕ ВМЕСТЕ).
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
