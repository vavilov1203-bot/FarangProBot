import os
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from telegram import (
    InlineKeyboardButton, 
    InlineKeyboardMarkup, 
    Update, 
    ReplyKeyboardRemove
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, ContextTypes
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "farangprobot.db")


# ==================== БАЗА ДАННЫХ ====================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS section_stats (
            section TEXT PRIMARY KEY,
            count INTEGER DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            section TEXT,
            visited_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def increment_stat(section: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO section_stats (section, count)
            VALUES (?, 1)
            ON CONFLICT(section) DO UPDATE SET count = count + 1
        """, (section,))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"increment_stat error: {e}", exc_info=True)


def log_user_visit(user_id: int, username: str, section: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_history (user_id, username, section, visited_at)
            VALUES (?, ?, ?, ?)
        """, (user_id, username or "NoUsername", section, datetime.now().isoformat()))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"log_user_visit error: {e}", exc_info=True)


def get_stats(period: str = "all") -> List[tuple]:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        if period == "today":
            today = datetime.now().date().isoformat()
            cursor.execute("""
                SELECT section, COUNT(*) as cnt 
                FROM user_history 
                WHERE DATE(visited_at) = ? 
                GROUP BY section ORDER BY cnt DESC
            """, (today,))
        elif period == "week":
            week_ago = (datetime.now() - timedelta(days=7)).isoformat()
            cursor.execute("""
                SELECT section, COUNT(*) as cnt 
                FROM user_history 
                WHERE visited_at >= ? 
                GROUP BY section ORDER BY cnt DESC
            """, (week_ago,))
        else:
            cursor.execute("SELECT section, count FROM section_stats ORDER BY count DESC")

        result = cursor.fetchall()
        conn.close()
        return result
    except Exception:
        return []


def get_top_users(limit: int = 10) -> List[tuple]:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT username, COUNT(*) as visits 
            FROM user_history 
            GROUP BY user_id 
            ORDER BY visits DESC LIMIT ?
        """, (limit,))
        result = cursor.fetchall()
        conn.close()
        return result
    except Exception:
        return []


def get_recent_visits(limit: int = 12) -> List[tuple]:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT username, section, visited_at 
            FROM user_history 
            ORDER BY visited_at DESC LIMIT ?
        """, (limit,))
        result = cursor.fetchall()
        conn.close()
        return result
    except Exception:
        return []


init_db()


# ==================== КЭШ ====================
_content_cache: Dict[str, str] = {}

def content_path(relative_path: str) -> str:
    return os.path.join(BASE_DIR, "content", relative_path)

def load_content(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        logger.warning(f"Файл не найден: {path}")
        return f"# Раздел в разработке\n\nФайл не найден: {path}"
    except Exception as e:
        logger.error(f"load_content error: {e}", exc_info=True)
        return "Ошибка загрузки контента."


def get_text(node: Dict[str, Any]) -> str:
    if "_text" in node:
        return node["_text"]
    if "_file" in node:
        key = node["_file"]
        if key in _content_cache:
            return _content_cache[key]
        content = load_content(content_path(key))
        _content_cache[key] = content
        return content
    return "Раздел в разработке"


# ==================== МЕНЮ ====================
MENU_TREE: Dict[str, Any] = {
    "_text": "Выбери пункт из меню 👇",
    "_children": {
        "🚨 Я только приехал / мне срочно": {
            "_file": "urgent/intro.md",
            "_children": {
                "✈️ Аэропорт": {"_file": "urgent/first_72_airport.md", "_children": {}},
                "📱 Связь": {"_file": "urgent/first_72_sim.md", "_children": {}},
                "💸 Деньги в первые дни": {"_file": "urgent/first_72_money.md", "_children": {}},
                "✅ Чек-лист 72 часа": {"_file": "urgent/first_day_checklist.md", "_children": {}},
                "⚠️ Таиланд — не рай": {"_file": "urgent/thailand_not_paradise.md", "_children": {}},
                "❌ Топ-5 ошибок первых дней": {"_file": "urgent/top5_mistakes.md", "_children": {}},
            },
        },
        "📄 Виза и легализация": {
            "_file": "visa/intro.md",
            "_children": {
                "❓ Какая виза мне подойдёт": {"_file": "visa/which_visa.md", "_children": {}},
                "ED — учебная": {
                    "_file": "visa/ed/intro.md",
                    "_children": {
                        "Кому подходит": {"_file": "visa/ed/who_fits.md", "_children": {}},
                        "Пошагово": {"_file": "visa/ed/steps.md", "_children": {}},
                        "Риски и ошибки": {"_file": "visa/ed/risks.md", "_children": {}},
                    },
                },
                "DTV — Digital Nomad": {
                    "_file": "visa/dtv/intro.md",
                    "_children": {
                        "Кому подходит": {"_file": "visa/dtv/who_fits.md", "_children": {}},
                        "Пошагово": {"_file": "visa/dtv/steps.md", "_children": {}},
                        "Риски и ошибки": {"_file": "visa/dtv/risks.md", "_children": {}},
                    },
                },
                "Семейная": {
                    "_file": "visa/family/intro.md",
                    "_children": {
                        "Основания": {"_file": "visa/family/grounds.md", "_children": {}},
                        "Пошагово": {"_file": "visa/family/steps.md", "_children": {}},
                        "Риски и ошибки": {"_file": "visa/family/risks.md", "_children": {}},
                    },
                },
                "Бизнес": {
                    "_file": "visa/business/intro.md",
                    "_children": {
                        "Кому подходит": {"_file": "visa/business/who_fits.md", "_children": {}},
                        "Пошагово": {"_file": "visa/business/steps.md", "_children": {}},
                        "Риски и ошибки": {"_file": "visa/business/risks.md", "_children": {}},
                    },
                },
                "Пенсионная": {
                    "_file": "visa/retirement/intro.md",
                    "_children": {
                        "Требования": {"_file": "visa/retirement/requirements.md", "_children": {}},
                        "Пошагово": {"_file": "visa/retirement/steps.md", "_children": {}},
                        "Риски": {"_file": "visa/retirement/risks.md", "_children": {}},
                    },
                },
                "Продление штампов": {
                    "_file": "visa/extensions/intro.md",
                    "_children": {
                        "Где и как": {"_file": "visa/extensions/where_how.md", "_children": {}},
                        "Сроки и штрафы": {"_file": "visa/extensions/deadlines_fines.md", "_children": {}},
                        "Типовые ошибки": {"_file": "visa/extensions/common_mistakes.md", "_children": {}},
                    },
                },
            },
        },
        "💸 Деньги и жильё": {
            "_file": "money_home/intro.md",
            "_children": {
                "💱 Обмен и деньги": {
                    "_file": "money_home/exchange/intro.md",
                    "_children": {
                        "Где менять выгодно": {"_file": "money_home/exchange/where_best.md", "_children": {}},
                        "Банки vs обменники": {"_file": "money_home/exchange/banks_vs_exchangers.md", "_children": {}},
                        "Безопасность": {"_file": "money_home/exchange/safety.md", "_children": {}},
                    },
                },
                "🏠 Аренда жилья": {
                    "_file": "money_home/rent/intro.md",
                    "_children": {
                        "Депозиты и контракты": {"_file": "money_home/rent/deposits_contracts.md", "_children": {}},
                        "Агент ≠ твой друг": {"_file": "money_home/rent/agent_not_friend.md", "_children": {}},
                        "Типовые схемы развода": {"_file": "money_home/rent/scams.md", "_children": {}},
                    },
                },
                "💳 Платежи и карты": {
                    "_file": "money_home/payments/intro.md",
                    "_children": {
                        "Нал vs безнал": {"_file": "money_home/payments/cash_vs_cashless.md", "_children": {}},
                        "Карты и блокировки": {"_file": "money_home/payments/cards_blocks.md", "_children": {}},
                        "Что говорить банку": {"_file": "money_home/payments/talk_to_bank.md", "_children": {}},
                    },
                },
            },
        },
        "⚠️ Реальность Таиланда": {
            "_file": "reality/intro.md",
            "_children": {
                "🧠 Ты всегда фаранг": {
                    "_file": "reality/farang/intro.md",
                    "_children": {
                        "Что это значит": {"_file": "reality/farang/what_it_means.md", "_children": {}},
                        "Улыбки ≠ дружба": {"_file": "reality/farang/smiles_not_friendship.md", "_children": {}},
                        "Где ошибаются чаще всего": {"_file": "reality/farang/common_errors.md", "_children": {}},
                    },
                },
                "🚩 Помогаторы": {
                    "_file": "reality/helpers/intro.md",
                    "_children": {
                        "Красные флаги": {"_file": "reality/helpers/red_flags.md", "_children": {}},
                        "Типовые схемы": {"_file": "reality/helpers/schemes.md", "_children": {}},
                        "Как отказывать": {"_file": "reality/helpers/how_to_say_no.md", "_children": {}},
                    },
                },
                "😵 Типичные ошибки": {
                    "_file": "reality/mistakes/intro.md",
                    "_children": {
                        "Алкоголь и агрессия": {"_file": "reality/mistakes/alcohol_aggression.md", "_children": {}},
                        "Байк и полиция": {"_file": "reality/mistakes/bike_police.md", "_children": {}},
                        "Нелегальная работа": {"_file": "reality/mistakes/illegal_work.md", "_children": {}},
                    },
                },
                "🙏 Культура и поведение": {
                    "_file": "reality/culture/intro.md",
                    "_children": {
                        "Король и религия": {"_file": "reality/culture/king_religion.md", "_children": {}},
                        "Храмы и одежда": {"_file": "reality/culture/temples_clothes.md", "_children": {}},
                        "Потеря лица": {"_file": "reality/culture/lose_face.md", "_children": {}},
                    },
                },
            },
        },
        "🆘 Нужна помощь": {
            "_file": "help/intro.md",
            "_children": {
                "🆘 Разобрать мою ситуацию": {"_file": "help/analyze_my_case.md", "_children": {}},
                "💬 Задать вопрос": {"_file": "help/ask_question.md", "_children": {}},
                "📋 Чек-листы": {
                    "_file": "help/checklists/intro.md",
                    "_children": {
                        "Первый месяц": {"_file": "help/checklists/first_month.md", "_children": {}},
                        "Аренда без потерь": {"_file": "help/checklists/rent_no_losses.md", "_children": {}},
                        "Виза без лишних расходов": {"_file": "help/checklists/visa_no_extra.md", "_children": {}},
                    },
                },
                "☕ Поддержать проект": {"_file": "help/support_project.md", "_children": {}},
            },
        },
    },
}


# ==================== УНИКАЛЬНЫЕ КОРОТКИЕ ID ====================
ID_COUNTER = 0
ID_TO_NODE: Dict[str, Dict[str, Any]] = {}
ID_TO_PATH: Dict[str, List[str]] = {}
ID_TO_NAME: Dict[str, str] = {}

def assign_node_ids(node: Dict[str, Any], current_path: List[str] = None):
    global ID_COUNTER
    if current_path is None:
        current_path = []

    for name, child in node.get("_children", {}).items():
        new_path = current_path + [name]
        node_id = f"m{ID_COUNTER:03d}"
        ID_COUNTER += 1

        ID_TO_NODE[node_id] = child
        ID_TO_PATH[node_id] = new_path
        ID_TO_NAME[node_id] = name

        assign_node_ids(child, new_path)

assign_node_ids(MENU_TREE)


def get_node_by_path(path: List[str]) -> Optional[Dict[str, Any]]:
    node = MENU_TREE
    try:
        for name in path:
            node = node["_children"][name]
        return node
    except (KeyError, TypeError):
        return None


def make_keyboard(node: Dict[str, Any], path: List[str]) -> InlineKeyboardMarkup:
    buttons = []
    for name in node.get("_children", {}):
        full_path = ".".join(path + [name])
        node_id = None
        for nid, p in ID_TO_PATH.items():
            if ".".join(p) == full_path:
                node_id = nid
                break

        if node_id:
            buttons.append([InlineKeyboardButton(name, callback_data=f"nav:{node_id}")])

    nav_row = []
    if path:
        nav_row.append(InlineKeyboardButton("⬅️ Назад", callback_data="action:back"))
    nav_row.append(InlineKeyboardButton("🏠 Главное меню", callback_data="action:home"))
    buttons.append(nav_row)

    return InlineKeyboardMarkup(buttons)


# ==================== ОБРАБОТЧИКИ ====================
async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, edit: bool = False):
    try:
        path: List[str] = context.user_data.get("path", [])
        node = get_node_by_path(path) or MENU_TREE
        text = get_text(node)
        keyboard = make_keyboard(node, path)

        if edit and update.callback_query:
            await update.callback_query.edit_message_text(text=text, reply_markup=keyboard, disable_web_page_preview=True)
        else:
            await update.effective_message.reply_text(text=text, reply_markup=keyboard, disable_web_page_preview=True)
    except Exception as e:
        logger.error(f"show_menu error: {e}", exc_info=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data["path"] = []
        # Удаляем старую ReplyKeyboard (если была)
        await update.effective_message.reply_text(
            "Загрузка меню...",
            reply_markup=ReplyKeyboardRemove()
        )
        await show_menu(update, context)
    except Exception as e:
        logger.error(f"start error: {e}", exc_info=True)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        data = query.data or ""
        path: List[str] = context.user_data.get("path", [])
        user = update.effective_user

        if data == "action:home":
            context.user_data["path"] = []
            await show_menu(update, context, edit=True)
            return

        if data == "action:back":
            if path:
                path.pop()
            context.user_data["path"] = path
            await show_menu(update, context, edit=True)
            return

        if data.startswith("nav:"):
            node_id = data[4:]
            if node_id in ID_TO_PATH:
                new_path = ID_TO_PATH[node_id]
                context.user_data["path"] = new_path
                section_name = ID_TO_NAME.get(node_id, "")

                try:
                    increment_stat(section_name)
                    log_user_visit(user.id, user.username, section_name)
                except Exception:
                    pass

                await show_menu(update, context, edit=True)
                return

        await query.edit_message_text("Ошибка навигации.")

    except Exception as e:
        logger.error(f"button_handler error: {e}", exc_info=True)


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        admin_id = os.getenv("ADMIN_USER_ID")
        if not admin_id or str(update.effective_user.id) != admin_id:
            await update.message.reply_text("⛔ Доступ запрещён.")
            return

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 Общая статистика", callback_data="admin:stats")],
            [InlineKeyboardButton("📅 За сегодня", callback_data="admin:today")],
            [InlineKeyboardButton("📆 За неделю", callback_data="admin:week")],
            [InlineKeyboardButton("👥 Топ пользователей", callback_data="admin:users")],
            [InlineKeyboardButton("🕒 Последние посещения", callback_data="admin:recent")],
        ])
        await update.message.reply_text("📊 **Админ-панель**", reply_markup=keyboard)
    except Exception as e:
        logger.error(f"admin_command error: {e}", exc_info=True)


async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        admin_id = os.getenv("ADMIN_USER_ID")
        if not admin_id or str(update.effective_user.id) != admin_id:
            await update.callback_query.edit_message_text("⛔ Доступ запрещён.")
            return

        query = update.callback_query
        await query.answer()
        data = query.data

        if data == "admin:stats":
            stats = get_stats("all")
            text = "📊 Общая статистика\n\n" + "\n".join([f"• {s}: {c}" for s, c in stats[:12]])
        elif data == "admin:today":
            stats = get_stats("today")
            text = "📅 Статистика за сегодня\n\n" + "\n".join([f"• {s}: {c}" for s, c in stats])
        elif data == "admin:week":
            stats = get_stats("week")
            text = "📆 Статистика за неделю\n\n" + "\n".join([f"• {s}: {c}" for s, c in stats])
        elif data == "admin:users":
            users = get_top_users(12)
            text = "👥 Топ пользователей\n\n" + "\n".join([f"• {u} — {c} посещений" for u, c in users])
        elif data == "admin:recent":
            visits = get_recent_visits(10)
            text = "🕒 Последние посещения\n\n" + "\n".join([f"• {u} → {s}" for u, s, _ in visits])
        else:
            text = "Неизвестная команда"

        await query.edit_message_text(text, reply_markup=query.message.reply_markup)

    except Exception as e:
        logger.error(f"admin_callback error: {e}", exc_info=True)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Глобальная ошибка:", exc_info=context.error)


# ==================== ЗАПУСК ====================
def main():
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("BOT_TOKEN не найден!")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_error_handler(error_handler)

    logger.info("FarangProBot запущен")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()