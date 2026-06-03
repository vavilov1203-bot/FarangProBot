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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_favorites_v2 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            node_id TEXT,
            section_name TEXT,
            added_at TEXT,
            UNIQUE(user_id, node_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS search_queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            query TEXT,
            results_count INTEGER,
            searched_at TEXT
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
        logger.error(f"increment_stat error: {e}")


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
        logger.error(f"log_user_visit error: {e}")


def log_search_query(user_id: int, query: str, results_count: int):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO search_queries (user_id, query, results_count, searched_at)
            VALUES (?, ?, ?, ?)
        """, (user_id, query, results_count, datetime.now().isoformat()))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"log_search_query error: {e}")


def add_to_favorites(user_id: int, node_id: str, section_name: str) -> bool:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO user_favorites_v2 (user_id, node_id, section_name, added_at)
            VALUES (?, ?, ?, ?)
        """, (user_id, node_id, section_name, datetime.now().isoformat()))
        added = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return added
    except Exception as e:
        logger.error(f"add_to_favorites error: {e}")
        return False


def get_user_favorites(user_id: int) -> List[tuple]:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT node_id, section_name FROM user_favorites_v2 
            WHERE user_id = ? ORDER BY added_at DESC
        """, (user_id,))
        result = cursor.fetchall()
        conn.close()
        return result
    except Exception:
        return []


def is_favorite(user_id: int, node_id: str) -> bool:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 1 FROM user_favorites_v2 
            WHERE user_id = ? AND node_id = ? LIMIT 1
        """, (user_id, node_id))
        result = cursor.fetchone() is not None
        conn.close()
        return result
    except Exception as e:
        logger.error(f"is_favorite error: {e}")
        return False


def remove_from_favorites(user_id: int, node_id: str) -> bool:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM user_favorites_v2 
            WHERE user_id = ? AND node_id = ?
        """, (user_id, node_id))
        removed = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return removed
    except Exception as e:
        logger.error(f"remove_from_favorites error: {e}")
        return False


def get_stats(period: str = "all") -> List[tuple]:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        if period == "today":
            today = datetime.now().date().isoformat()
            cursor.execute(
                "SELECT section, COUNT(*) FROM user_history WHERE DATE(visited_at)=? GROUP BY section ORDER BY COUNT(*) DESC",
                (today,)
            )
        elif period == "week":
            week_ago = (datetime.now() - timedelta(days=7)).isoformat()
            cursor.execute(
                "SELECT section, COUNT(*) FROM user_history WHERE visited_at >= ? GROUP BY section ORDER BY COUNT(*) DESC",
                (week_ago,)
            )
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
        cursor.execute(
            "SELECT username, COUNT(*) FROM user_history GROUP BY user_id ORDER BY COUNT(*) DESC LIMIT ?",
            (limit,)
        )
        result = cursor.fetchall()
        conn.close()
        return result
    except Exception:
        return []


def get_recent_visits(limit: int = 12) -> List[tuple]:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT username, section, visited_at FROM user_history ORDER BY visited_at DESC LIMIT ?",
            (limit,)
        )
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
            content = file.read()
            return content if content.strip() else "Раздел находится в разработке."
    except FileNotFoundError:
        logger.warning(f"Файл не найден: {path}")
        return "Раздел находится в разработке."
    except Exception as e:
        logger.error(f"load_content error: {e}")
        return "Раздел находится в разработке."


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
    return "Раздел находится в разработке."


# ==================== МЕНЮ ====================
MENU_TREE: Dict[str, Any] = {
    "_text": "Выбери пункт из меню 👇",
    "_children": {
        "🚨 Я только приехал": {
            "_file": "urgent/intro.md",
            "_children": {
                "✈️ Аэропорт и первые часы": {"_file": "urgent/first_72_airport.md", "_children": {}},
                "📱 Связь: SIM / eSIM": {"_file": "urgent/first_72_sim.md", "_children": {}},
                "💸 Деньги в первые дни": {"_file": "urgent/first_72_money.md", "_children": {}},
                "✅ Чек-лист 72 часа": {"_file": "urgent/first_day_checklist.md", "_children": {}},
                "❌ Топ-5 ошибок первых дней": {"_file": "urgent/top5_mistakes.md", "_children": {}},
                "🧳 С семьёй и/или питомцем": {"_file": "urgent/family_pets.md", "_children": {}},
            },
        },
        "📄 Виза и легализация": {
            "_file": "visa/intro.md",
            "_children": {
                "📚 Туристические визы": {"_file": "visa/tourist.md", "_children": {}},
                "🧑‍🎓 Учебные визы ED": {"_file": "visa/ed.md", "_children": {}},
                "💼 Рабочие и бизнес-визы": {"_file": "visa/business_work.md", "_children": {}},
                "❤️ Семейные и пенсионные": {"_file": "visa/family_retirement.md", "_children": {}},
                "👑 Thailand Elite / Privilege": {"_file": "visa/elite_privilege.md", "_children": {}},
                "⚙️ Полезное: TM30, Re-entry, overstay": {"_file": "visa/useful.md", "_children": {}},
            },
        },
        "🏠 Жильё и транспорт": {
            "_file": "housing_transport/intro.md",
            "_children": {
                "🏙 Кондо / квартиры": {"_file": "housing_transport/condos.md", "_children": {}},
                "🏡 Дома / виллы": {"_file": "housing_transport/houses_villas.md", "_children": {}},
                "🚗 Автомобили": {"_file": "housing_transport/cars.md", "_children": {}},
                "🛵 Байки и мотоциклы": {"_file": "housing_transport/bikes.md", "_children": {}},
                "⚙️ Полезное по аренде": {"_file": "housing_transport/useful_rent.md", "_children": {}},
            },
        },
        "💬 Как тут жить": {
            "_file": "life/intro.md",
            "_children": {
                "💳 Банки и деньги": {"_file": "life/banks_money.md", "_children": {}},
                "💊 Медицина и страховка": {"_file": "life/medicine_insurance.md", "_children": {}},
                "🏫 Школы и образование": {"_file": "life/schools_education.md", "_children": {}},
                "📱 Связь и интернет": {"_file": "life/mobile_internet.md", "_children": {}},
                "🍛 Быт и продукты": {"_file": "life/food_daily_life.md", "_children": {}},
                "💼 Работа и налоги": {"_file": "life/work_taxes.md", "_children": {}},
            },
        },
        "🐾 Животные и переезд": {
            "_file": "pets_relocation/intro.md",
            "_children": {
                "✈️ Ввоз питомца в Таиланд": {"_file": "pets_relocation/import_pet.md", "_children": {}},
                "📄 Документы и требования": {"_file": "pets_relocation/documents_requirements.md", "_children": {}},
                "🏥 Ветеринария и уход": {"_file": "pets_relocation/vet_care.md", "_children": {}},
                "🌍 Вывоз из Таиланда": {"_file": "pets_relocation/export_from_thailand.md", "_children": {}},
                "🐈 Практические советы": {"_file": "pets_relocation/practical_tips.md", "_children": {}},
            },
        },
        "⚠️ Поведение и культура": {
            "_file": "culture/intro.md",
            "_children": {
                "👣 Прежде чем ты начнёшь": {"_file": "culture/before_you_start.md", "_children": {}},
                "🙏 Тайская культура и табу": {"_file": "culture/thai_culture_taboo.md", "_children": {}},
                "😑 Типичные ошибки фарангов": {"_file": "culture/farang_mistakes.md", "_children": {}},
                "💡 Как вызывать уважение": {"_file": "culture/respect.md", "_children": {}},
                "🧘 Сабай-сабай": {"_file": "culture/sabai_sabai.md", "_children": {}},
            },
        },
        "🆘 Нужна помощь": {
            "_file": "help/intro.md",
            "_children": {
                "🔍 Разобрать мою ситуацию": {"_file": "help/analyze_my_case.md", "_children": {}},
                "💬 Задать вопрос": {"_file": "help/ask_question.md", "_children": {}},
                "📋 Чек-листы и гайды": {"_file": "help/checklists_guides.md", "_children": {}},
                "❤️ Поддержать проект": {"_file": "help/support_project.md", "_children": {}},
            },
        },
        "⚙️ О боте": {
            "_file": "about/intro.md",
            "_children": {
                "Что такое FarangProBot": {"_file": "about/what_is_it.md", "_children": {}},
                "Кто делает проект": {"_file": "about/author.md", "_children": {}},
                "Обратная связь": {"_file": "about/feedback.md", "_children": {}},
                "Поддержать проект": {"_file": "help/support_project.md", "_children": {}},
            },
        },
    },
}


# ==================== ID СИСТЕМА ====================
ID_COUNTER = 0
ID_TO_NODE: Dict[str, Dict[str, Any]] = {}
ID_TO_PATH: Dict[str, List[str]] = {}
ID_TO_NAME: Dict[str, str] = {}
PATH_TO_ID: Dict[str, str] = {}


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
        PATH_TO_ID[".".join(new_path)] = node_id

        assign_node_ids(child, new_path)


assign_node_ids(MENU_TREE)


HELP_ANALYZE_PATH = ["🆘 Нужна помощь", "🔍 Разобрать мою ситуацию"]
HELP_ANALYZE_ID = PATH_TO_ID.get(".".join(HELP_ANALYZE_PATH))


def get_node_by_path(path: List[str]) -> Optional[Dict[str, Any]]:
    node = MENU_TREE
    try:
        for name in path:
            node = node["_children"][name]
        return node
    except (KeyError, TypeError):
        return None


def make_breadcrumbs(path: List[str]) -> str:
    if not path:
        return ""
    parts = ["🏠 Главное меню"]
    for name in path:
        parts.append(name)
    return " → ".join(parts) + "\n\n"


def make_keyboard(
    node: Dict[str, Any], path: List[str], user_id: Optional[int] = None
) -> InlineKeyboardMarkup:
    buttons: List[List[InlineKeyboardButton]] = []

    for name in node.get("_children", {}):
        full_path_key = ".".join(path + [name])
        node_id = PATH_TO_ID.get(full_path_key)
        if node_id:
            buttons.append([
                InlineKeyboardButton(name, callback_data=f"nav:{node_id}")
            ])

    important = [
        "📄 Виза и легализация",
        "🏠 Жильё и транспорт",
        "💬 Как тут жить",
        "🐾 Животные и переезд",
        "⚠️ Поведение и культура",
    ]
    if path and (path[0] in important or any(s in path for s in important)):
        if HELP_ANALYZE_ID:
            buttons.append([
                InlineKeyboardButton("🆘 Разобрать мою ситуацию", callback_data=f"nav:{HELP_ANALYZE_ID}")
            ])

    if path and user_id:
        full_path_key = ".".join(path)
        node_id = PATH_TO_ID.get(full_path_key)
        if node_id:
            if is_favorite(user_id, node_id):
                buttons.append([
                    InlineKeyboardButton("🗑 Удалить из избранного", callback_data="action:unfav")
                ])
            else:
                buttons.append([
                    InlineKeyboardButton("⭐ В избранное", callback_data="action:fav")
                ])
    elif path:
        buttons.append([
            InlineKeyboardButton("⭐ В избранное", callback_data="action:fav")
        ])

    if not path:
        buttons.append([
            InlineKeyboardButton("🔍 Поиск", callback_data="action:search_info"),
            InlineKeyboardButton("⭐ Избранное", callback_data="action:show_favs")
        ])

    if path:
        nav_row = [
            InlineKeyboardButton("⬅️ Назад", callback_data="action:back"),
            InlineKeyboardButton("🏠 Главное меню", callback_data="action:home")
        ]
        buttons.append(nav_row)

    return InlineKeyboardMarkup(buttons)


# ==================== ОБРАБОТЧИКИ ====================
async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        path: List[str] = context.user_data.get("path", [])
        node = get_node_by_path(path) or MENU_TREE
        breadcrumbs = make_breadcrumbs(path)
        text = breadcrumbs + get_text(node)

        if len(text) > 3900:
            text = text[:3900] + "\n\n…"

        user_id = update.effective_user.id if update and update.effective_user else None
        keyboard = make_keyboard(node, path, user_id)

        await update.effective_message.reply_text(
            text=text,
            reply_markup=keyboard,
            disable_web_page_preview=True
        )
    except Exception as e:
        logger.error(f"show_menu error: {e}", exc_info=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data["path"] = []
        await update.effective_message.reply_text(
            "Farang Pro\n\n"
            "Практичный помощник по жизни в Таиланде:\n"
            "визы, жильё, деньги, безопасность, адаптация и типичные ошибки.\n\n"
            "Выбери, с чего начать:",
            reply_markup=ReplyKeyboardRemove()
        )
        await show_menu(update, context)
    except Exception as e:
        logger.error(f"start error: {e}", exc_info=True)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        data = query.data or ""
        logger.info(f"Callback data: {data}")

        path: List[str] = context.user_data.get("path", [])
        user = update.effective_user

        if data.startswith("admin:"):
            await admin_callback(update, context)
            return

        await query.answer()

        if data == "action:home":
            context.user_data["path"] = []
            await show_menu(update, context)
            return

        if data == "action:back":
            if path:
                path.pop()
            context.user_data["path"] = path
            await show_menu(update, context)
            return

        if data == "action:fav":
            if path:
                section_name = path[-1]
                full_path_key = ".".join(path)
                node_id = PATH_TO_ID.get(full_path_key)
                if node_id:
                    added = add_to_favorites(user.id, node_id, section_name)
                    msg = "⭐ Добавлено в избранное" if added else "⭐ Уже есть в избранном"
                    await query.answer(msg, show_alert=True)
                    await show_menu(update, context)
            return

        if data == "action:unfav":
            if path:
                full_path_key = ".".join(path)
                node_id = PATH_TO_ID.get(full_path_key)
                if node_id:
                    removed = remove_from_favorites(user.id, node_id)
                    msg = "🗑 Удалено из избранного" if removed else "🗑 Не было в избранном"
                    await query.answer(msg, show_alert=True)
                    await show_menu(update, context)
            return

        if data == "action:show_favs":
            favs = get_user_favorites(user.id)
            if not favs:
                await query.answer("У вас пока нет избранных разделов.", show_alert=True)
                return
            keyboard = [
                [InlineKeyboardButton(name, callback_data=f"nav:{nid}")] for nid, name in favs
            ]
            await update.effective_message.reply_text(
                "⭐ Ваше избранное:\n\nВыберите раздел для перехода:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return

        if data == "action:search_info":
            await query.answer(
                "Для поиска используй команду:\n/search ваш запрос\n\nПример: /search виза DTV",
                show_alert=True
            )
            return

        if data.startswith("nav:"):
            node_id = data[4:]
            if node_id in ID_TO_PATH:
                new_path = ID_TO_PATH[node_id]
                node = get_node_by_path(new_path)
                if node is not None:
                    context.user_data["path"] = new_path
                    section_name = ID_TO_NAME.get(node_id, "")
                    logger.info(f"Opening path: {new_path} | node_id: {node_id}")
                    try:
                        increment_stat(section_name)
                        log_user_visit(user.id, user.username, section_name)
                    except Exception:
                        pass
                    await show_menu(update, context)
                    return
                else:
                    await query.answer("Раздел обновился. Нажмите /start", show_alert=True)
                    return
            else:
                await query.answer("Раздел обновился. Нажмите /start", show_alert=True)
                return

        await query.answer("Неизвестная команда. Используйте /start", show_alert=True)

    except Exception as e:
        logger.error(f"button_handler error: {e}", exc_info=True)


async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query_text = " ".join(context.args).strip().lower()
        if not query_text:
            await update.effective_message.reply_text("Используйте: /search <запрос>")
            return

        results = []
        for node_id, node in ID_TO_NODE.items():
            name = ID_TO_NAME.get(node_id, "")
            if query_text in name.lower() or query_text in get_text(node).lower():
                results.append((node_id, name))

        log_search_query(update.effective_user.id, query_text, len(results))

        if not results:
            await update.effective_message.reply_text("Ничего не найдено.")
            return

        keyboard = [
            [InlineKeyboardButton(name, callback_data=f"nav:{nid}")] for nid, name in results[:15]
        ]
        await update.effective_message.reply_text(
            "Результаты поиска:", reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        logger.error(f"search_command error: {e}", exc_info=True)


async def favorites_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        favs = get_user_favorites(update.effective_user.id)
        if not favs:
            await update.effective_message.reply_text("У вас пока нет избранных разделов.")
            return

        keyboard = [
            [InlineKeyboardButton(name, callback_data=f"nav:{nid}")] for nid, name in favs
        ]
        await update.effective_message.reply_text(
            "⭐ Ваше избранное:", reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        logger.error(f"favorites_command error: {e}", exc_info=True)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = (
            "Farang Pro — практичный гид по реальной жизни в Таиланде.\n\n"
            "📌 Доступные команды:\n"
            "/start — главное меню\n"
            "/search <текст> — поиск по разделам\n"
            "/favorites — ваше избранное\n"
            "/help — эта справка\n\n"
            "В главном меню есть быстрые кнопки «🔍 Поиск» и «⭐ Избранное».\n"
            "Добавляй важные разделы в избранное — потом быстро возвращайся.\n\n"
            "Мы за трезвый взгляд и реальные действия. Без иллюзий и кликбейта."
        )
        await update.effective_message.reply_text(text)
    except Exception as e:
        logger.error(f"help_command error: {e}", exc_info=True)


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = os.getenv("ADMIN_USER_ID")
    if not admin_id or str(update.effective_user.id) != admin_id:
        await update.effective_message.reply_text("⛔ Доступ запрещён.")
        return

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Общая статистика", callback_data="admin:stats")],
        [InlineKeyboardButton("📅 За сегодня", callback_data="admin:today")],
        [InlineKeyboardButton("📆 За неделю", callback_data="admin:week")],
        [InlineKeyboardButton("👥 Топ пользователей", callback_data="admin:users")],
        [InlineKeyboardButton("🕒 Последние посещения", callback_data="admin:recent")],
    ])
    await update.effective_message.reply_text("📊 Админ-панель", reply_markup=keyboard)


async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = os.getenv("ADMIN_USER_ID")
    if not admin_id or str(update.effective_user.id) != admin_id:
        try:
            await update.callback_query.answer("⛔ Доступ запрещён.", show_alert=True)
        except:
            pass
        return

    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "admin:stats":
        stats = get_stats("all")
        text = "📊 Общая статистика\n\n" + ("\n".join([f"• {s}: {c}" for s, c in stats[:15]]) if stats else "Пока нет данных.")
    elif data == "admin:today":
        stats = get_stats("today")
        text = "📅 Статистика за сегодня\n\n" + ("\n".join([f"• {s}: {c}" for s, c in stats]) if stats else "Пока нет данных.")
    elif data == "admin:week":
        stats = get_stats("week")
        text = "📆 Статистика за неделю\n\n" + ("\n".join([f"• {s}: {c}" for s, c in stats]) if stats else "Пока нет данных.")
    elif data == "admin:users":
        users = get_top_users(15)
        text = "👥 Топ пользователей\n\n" + ("\n".join([f"• {u} — {c} посещений" for u, c in users]) if users else "Пока нет данных.")
    elif data == "admin:recent":
        visits = get_recent_visits(12)
        text = "🕒 Последние посещения\n\n" + ("\n".join([f"• {u} → {s}" for u, s, _ in visits]) if visits else "Пока нет данных.")
    else:
        text = "Неизвестная команда"

    await update.effective_message.reply_text(text, reply_markup=query.message.reply_markup)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Глобальная ошибка:", exc_info=context.error)


# ==================== ЗАПУСК ====================
def main():
    token = (os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN") or "").strip()
    if not token:
        raise RuntimeError("BOT_TOKEN / TELEGRAM_BOT_TOKEN не найден!")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(CommandHandler("search", search_command))
    app.add_handler(CommandHandler("favorites", favorites_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_error_handler(error_handler)

    logger.info("FarangProBot v2.0 запущен (только reply_text, без редактирования)")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()