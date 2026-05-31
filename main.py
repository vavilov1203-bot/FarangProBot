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
        return f"# Раздел в разработке\n\nФайл не найден:\n{path}"


BTN_BACK = "⬅️ Назад"
BTN_HOME = "🏠 Главное меню"


MENU_TREE: Dict[str, Any] = {
    "_text": "Выбери пункт из меню 👇",
    "_children": {
        # ==========================================================
        # 🚨 Я только приехал / мне срочно
        # ==========================================================
        "🚨 Я только приехал / мне срочно": {
           "_text": load_content(content_path("urgent/intro.md")),
           "_children": {
               "✈️ Аэропорт": {
                  "_text": load_content(content_path("urgent/first_72_airport.md")),
                  "_children": {},
           },
           "📱 Связь": {
               "_text": load_content(content_path("urgent/first_72_sim.md")),
               "_children": {},
           },
           "💸 Деньги в первые дни": {
               "_text": load_content(content_path("urgent/first_72_money.md")),
               "_children": {},
           },
           "🚕 Как уехать из аэропорта": {
               "_text": load_content(content_path("urgent/first_72_transport.md")),
               "_children": {},
           },
           "🏠 Первое жильё": {
               "_text": load_content(content_path("urgent/first_72_housing.md")),
               "_children": {},
           },
           "✅ Чек-лист 72 часа": {
               "_text": load_content(content_path("urgent/first_day_checklist.md")),
               "_children": {},
           },
           "⚠️ Таиланд — не рай": {
               "_text": load_content(content_path("urgent/thailand_not_paradise.md")),
               "_children": {},
           },
           "❌ Топ-5 ошибок первых дней": {
               "_text": load_content(content_path("urgent/top5_mistakes.md")),
               "_children": {},
           },
              
       },
   },
        # ==========================================================
        # 📄 Виза и легализация
        # ==========================================================
        "📄 Виза и легализация": {
            "_text": load_content(content_path("visa/intro.md")),
            "_children": {
                "❓ Какая виза мне подойдёт": {
                    "_text": load_content(content_path("visa/which_visa.md")),
                    "_children": {},
                },

                "ED — учебная": {
                    "_text": load_content(content_path("visa/ed/intro.md")),
                    "_children": {
                        "Кому подходит": {"_text": load_content(content_path("visa/ed/who_fits.md")), "_children": {}},
                        "Пошагово": {"_text": load_content(content_path("visa/ed/steps.md")), "_children": {}},
                        "Риски и ошибки": {"_text": load_content(content_path("visa/ed/risks.md")), "_children": {}},
                    },
                },

                "DTV — Digital Nomad": {
                    "_text": load_content(content_path("visa/dtv/intro.md")),
                    "_children": {
                        "Кому подходит": {"_text": load_content(content_path("visa/dtv/who_fits.md")), "_children": {}},
                        "Пошагово": {"_text": load_content(content_path("visa/dtv/steps.md")), "_children": {}},
                        "Риски и ошибки": {"_text": load_content(content_path("visa/dtv/risks.md")), "_children": {}},
                    },
                },

                "Семейная": {
                    "_text": load_content(content_path("visa/family/intro.md")),
                    "_children": {
                        "Основания": {"_text": load_content(content_path("visa/family/grounds.md")), "_children": {}},
                        "Пошагово": {"_text": load_content(content_path("visa/family/steps.md")), "_children": {}},
                        "Риски и ошибки": {"_text": load_content(content_path("visa/family/risks.md")), "_children": {}},
                    },
                },

                "Бизнес": {
                    "_text": load_content(content_path("visa/business/intro.md")),
                    "_children": {
                        "Кому подходит": {"_text": load_content(content_path("visa/business/who_fits.md")), "_children": {}},
                        "Пошагово": {"_text": load_content(content_path("visa/business/steps.md")), "_children": {}},
                        "Риски и ошибки": {"_text": load_content(content_path("visa/business/risks.md")), "_children": {}},
                    },
                },

                "Пенсионная": {
                    "_text": load_content(content_path("visa/retirement/intro.md")),
                    "_children": {
                        "Требования": {"_text": load_content(content_path("visa/retirement/requirements.md")), "_children": {}},
                        "Пошагово": {"_text": load_content(content_path("visa/retirement/steps.md")), "_children": {}},
                        "Риски": {"_text": load_content(content_path("visa/retirement/risks.md")), "_children": {}},
                    },
                },

                "Продление штампов": {
                    "_text": load_content(content_path("visa/extensions/intro.md")),
                    "_children": {
                        "Где и как": {"_text": load_content(content_path("visa/extensions/where_how.md")), "_children": {}},
                        "Сроки и штрафы": {"_text": load_content(content_path("visa/extensions/deadlines_fines.md")), "_children": {}},
                        "Типовые ошибки": {"_text": load_content(content_path("visa/extensions/common_mistakes.md")), "_children": {}},
                    },
                },
            },
        },

        # ==========================================================
        # 💸 Деньги и жильё
        # ==========================================================
        "💸 Деньги и жильё": {
            "_text": load_content(content_path("money_home/intro.md")),
            "_children": {
                "💱 Обмен и деньги": {
                    "_text": load_content(content_path("money_home/exchange/intro.md")),
                    "_children": {
                        "Где менять выгодно": {"_text": load_content(content_path("money_home/exchange/where_best.md")), "_children": {}},
                        "Банки vs обменники": {"_text": load_content(content_path("money_home/exchange/banks_vs_exchangers.md")), "_children": {}},
                        "Безопасность": {"_text": load_content(content_path("money_home/exchange/safety.md")), "_children": {}},
                    },
                },

                "🏠 Аренда жилья": {
                    "_text": load_content(content_path("money_home/rent/intro.md")),
                    "_children": {
                        "Депозиты и контракты": {"_text": load_content(content_path("money_home/rent/deposits_contracts.md")), "_children": {}},
                        "Агент ≠ твой друг": {"_text": load_content(content_path("money_home/rent/agent_not_friend.md")), "_children": {}},
                        "Типовые схемы развода": {"_text": load_content(content_path("money_home/rent/scams.md")), "_children": {}},
                    },
                },

                "💳 Платежи и карты": {
                    "_text": load_content(content_path("money_home/payments/intro.md")),
                    "_children": {
                        "Нал vs безнал": {"_text": load_content(content_path("money_home/payments/cash_vs_cashless.md")), "_children": {}},
                        "Карты и блокировки": {"_text": load_content(content_path("money_home/payments/cards_blocks.md")), "_children": {}},
                        "Что говорить банку": {"_text": load_content(content_path("money_home/payments/talk_to_bank.md")), "_children": {}},
                    },
                },
            },
        },

        # ==========================================================
        # ⚠️ Реальность Таиланда
        # ==========================================================
        "⚠️ Реальность Таиланда": {
            "_text": load_content(content_path("reality/intro.md")),
            "_children": {
                "🧠 Ты всегда фаранг": {
                    "_text": load_content(content_path("reality/farang/intro.md")),
                    "_children": {
                        "Что это значит": {"_text": load_content(content_path("reality/farang/what_it_means.md")), "_children": {}},
                        "Улыбки ≠ дружба": {"_text": load_content(content_path("reality/farang/smiles_not_friendship.md")), "_children": {}},
                        "Где ошибаются чаще всего": {"_text": load_content(content_path("reality/farang/common_errors.md")), "_children": {}},
                    },
                },

                "🚩 Помогаторы": {
                    "_text": load_content(content_path("reality/helpers/intro.md")),
                    "_children": {
                        "Красные флаги": {"_text": load_content(content_path("reality/helpers/red_flags.md")), "_children": {}},
                        "Типовые схемы": {"_text": load_content(content_path("reality/helpers/schemes.md")), "_children": {}},
                        "Как отказывать": {"_text": load_content(content_path("reality/helpers/how_to_say_no.md")), "_children": {}},
                    },
                },

                "😵 Типичные ошибки": {
                    "_text": load_content(content_path("reality/mistakes/intro.md")),
                    "_children": {
                        "Алкоголь и агрессия": {"_text": load_content(content_path("reality/mistakes/alcohol_aggression.md")), "_children": {}},
                        "Байк и полиция": {"_text": load_content(content_path("reality/mistakes/bike_police.md")), "_children": {}},
                        "Нелегальная работа": {"_text": load_content(content_path("reality/mistakes/illegal_work.md")), "_children": {}},
                    },
                },

                "🙏 Культура и поведение": {
                    "_text": load_content(content_path("reality/culture/intro.md")),
                    "_children": {
                        "Король и религия": {"_text": load_content(content_path("reality/culture/king_religion.md")), "_children": {}},
                        "Храмы и одежда": {"_text": load_content(content_path("reality/culture/temples_clothes.md")), "_children": {}},
                        "Потеря лица": {"_text": load_content(content_path("reality/culture/lose_face.md")), "_children": {}},
                    },
                },
            },
        },

        # ==========================================================
        # 🆘 Нужна помощь
        # ==========================================================
        "🆘 Нужна помощь": {
            "_text": load_content(content_path("help/intro.md")),
            "_children": {
                "🆘 Разобрать мою ситуацию": {
                    "_text": load_content(content_path("help/analyze_my_case.md")),
                    "_children": {},
                },
                "💬 Задать вопрос": {
                    "_text": load_content(content_path("help/ask_question.md")),
                    "_children": {},
                },
                "📋 Чек-листы": {
                    "_text": load_content(content_path("help/checklists/intro.md")),
                    "_children": {
                        "Первый месяц": {"_text": load_content(content_path("help/checklists/first_month.md")), "_children": {}},
                        "Аренда без потерь": {"_text": load_content(content_path("help/checklists/rent_no_losses.md")), "_children": {}},
                        "Виза без лишних расходов": {"_text": load_content(content_path("help/checklists/visa_no_extra.md")), "_children": {}},
                    },
                },
                "☕ Поддержать проект": {
                    "_text": load_content(content_path("help/support_project.md")),
                    "_children": {},
                },
            },
        },
    },
}


def get_node_by_path(path: List[str]) -> Dict[str, Any]:
    node = MENU_TREE
    for step in path:
        node = node["_children"][step]
    return node


def make_keyboard(node: Dict[str, Any], is_root: bool) -> ReplyKeyboardMarkup:
    buttons = list(node.get("_children", {}).keys())
    rows = [[b] for b in buttons]

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

    if txt in children:
        path.append(txt)
        context.user_data["path"] = path
        await show_menu(update, context)
        return

    await update.message.reply_text("Пожалуйста, используй кнопки 👇")


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
