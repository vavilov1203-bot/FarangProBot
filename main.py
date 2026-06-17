import os
import logging
import sqlite3
import hashlib
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

CURRENT_MENU_VERSION = "v5"


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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            action_type TEXT,
            topic TEXT,
            created_at TEXT
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


def save_lead(user_id: int, username: str, action_type: str, topic: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO leads (user_id, username, action_type, topic, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, username or "NoUsername", action_type, topic, datetime.now().isoformat()))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"save_lead error: {e}")


def get_leads(limit: int = 20) -> List[tuple]:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT username, action_type, topic, created_at FROM leads ORDER BY created_at DESC LIMIT ?",
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


_STUB_MARKERS = ("Этот раздел ещё заполняется", "Раздел находится в разработке")

def load_content(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as file:
            content = file.read()
        if not content.strip():
            return "🔧 Раздел готовится. Загляни позже."
        if any(marker in content for marker in _STUB_MARKERS):
            return "🔧 Раздел готовится. Мы работаем над этим материалом — загляни позже."
        return content
    except FileNotFoundError:
        logger.warning(f"Файл не найден: {path}")
        return "🔧 Раздел готовится. Загляни позже."
    except Exception as e:
        logger.error(f"load_content error: {e}")
        return "🔧 Ошибка загрузки раздела."


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
    return "🔧 Раздел готовится. Загляни позже."


# ==================== МЕНЮ ====================
MENU_TREE: Dict[str, Any] = {
    "_text": "Выбери раздел 👇\n\n🧭 Не знаешь с чего начать? Нажми «Моя ситуация».",
    "_children": {
        "🧭 Моя ситуация / С чего начать": {
            "_text": "Выбери свою ситуацию — покажу, с чего начать 👇",
            "_children": {
                "Я планирую переезд": {
                    "_text": (
                        "🗺 Планируешь переезд в Таиланд\n\n"
                        "С чего начать:\n\n"
                        "1. Определись с визой — от этого зависит всё остальное.\n"
                        "2. Изучи районы, прежде чем искать жильё.\n"
                        "3. Не принимай необратимых решений до первого визита.\n\n"
                        "📌 Полезные разделы в главном меню:\n"
                        "→ «Визы и легализация» — какая виза тебе подходит\n"
                        "→ «Жильё и транспорт» — как устроена аренда\n"
                        "→ «Как тут жить» — медицина, связь, школы"
                    ),
                    "_children": {}
                },
                "Я только приехал": {
                    "_text": (
                        "🚨 Ты только что прилетел\n\n"
                        "Главное сейчас — не торопиться.\n\n"
                        "1. Свяжись с близкими — сообщи, что долетел.\n"
                        "2. Купи SIM или подключи eSIM.\n"
                        "3. Обменяй немного батов.\n"
                        "4. Доберись до отеля и отдохни.\n"
                        "5. Первые важные решения — только после нормального сна.\n\n"
                        "📌 Открой раздел «🚨 Я только приехал» — там все подробные инструкции."
                    ),
                    "_children": {}
                },
                "Мне нужна виза": {
                    "_text": (
                        "📄 Нужна виза в Таиланд\n\n"
                        "Основные варианты:\n\n"
                        "• Туристическая — до 60 дней, можно продлить один раз\n"
                        "• ED (учебная) — от 1 года, нужна аккредитованная школа\n"
                        "• DTV — для цифровых кочевников и фрилансеров\n"
                        "• Бизнес-виза — для тех, кто работает или открывает компанию\n"
                        "• Семейная — если есть тайский супруг или ребёнок\n"
                        "• Пенсионная — от 50 лет\n\n"
                        "📌 Открой раздел «📄 Визы и легализация» — подробности по каждому типу."
                    ),
                    "_children": {}
                },
                "Ищу жильё": {
                    "_text": (
                        "🏠 Ищешь жильё в Таиланде\n\n"
                        "Главные правила:\n\n"
                        "• Не снимай на долгий срок сразу после прилёта\n"
                        "• Первые 7–10 дней — временное жильё\n"
                        "• Сначала осмотри район, потом — квартиру\n"
                        "• Риелтор не твой друг, даже если говорит по-русски\n"
                        "• Всегда читай договор до подписания\n\n"
                        "📌 Разделы в меню:\n"
                        "→ «Жильё и транспорт» — типы жилья и аренда\n"
                        "→ «Деньги и банки» → «Аренда» — депозиты, схемы развода"
                    ),
                    "_children": {}
                },
                "Переезжаю с семьёй": {
                    "_text": (
                        "👨‍👩‍👧 Переезжаешь с семьёй\n\n"
                        "Что важно учесть:\n\n"
                        "• Виза для детей оформляется отдельно\n"
                        "• Школы в Таиланде — международные (дорогие) и тайские\n"
                        "• Медицина — оформи страховку на всех членов семьи\n"
                        "• Выбирай район с учётом школы, больницы, магазинов\n\n"
                        "📌 Разделы в меню:\n"
                        "→ «Визы» — семейные визы\n"
                        "→ «Как тут жить» — школы, медицина"
                    ),
                    "_children": {}
                },
                "Переезжаю с животным": {
                    "_text": (
                        "🐾 Везёшь питомца в Таиланд\n\n"
                        "Минимум, что нужно знать:\n\n"
                        "• Нужны: справка от ветеринара, чип, прививки (в т.ч. от бешенства)\n"
                        "• Документы оформляются за несколько недель до вылета\n"
                        "• Таиланд разрешает ввоз кошек и собак при соблюдении требований\n"
                        "• В туристических районах есть хорошие ветклиники\n\n"
                        "📌 Открой раздел «🐾 Животные и переезд» — полный список документов."
                    ),
                    "_children": {}
                },
                "Хочу работать / открыть бизнес": {
                    "_text": (
                        "💼 Работа и бизнес в Таиланде\n\n"
                        "Что важно понять сразу:\n\n"
                        "• Работать без разрешения на работу (Work Permit) — нелегально\n"
                        "• Это касается в том числе удалённой работы\n"
                        "• Для открытия бизнеса нужна компания Thai Ltd или BOI\n"
                        "• DTV-виза — для фрилансеров, не даёт право работать на тайских работодателей\n\n"
                        "📌 Разделы в меню:\n"
                        "→ «Визы» — DTV и бизнес-виза\n"
                        "→ «Как тут жить» → «Работа и налоги»"
                    ),
                    "_children": {}
                },
                "У меня возникла проблема": {
                    "_text": (
                        "🆘 Возникла проблема\n\n"
                        "Частые ситуации:\n\n"
                        "• Просрочил визу → «Визы» → «Продление и штрафы»\n"
                        "• Проблема с жильём → «Деньги и банки» → «Аренда»\n"
                        "• Заблокировали карту → «Деньги и банки» → «Карты и платежи»\n"
                        "• Попал в ДТП или конфликт → «Реальность Таиланда»\n"
                        "• Другое → «Нужна помощь» → «Задать вопрос»"
                    ),
                    "_children": {}
                },
            }
        },
        "🚨 Я только приехал": {
            "_file": "urgent/intro.md",
            "_children": {
                "✈️ Аэропорт и первые часы": {"_file": "urgent/first_72_airport.md", "_children": {}},
                "🚕 Транспорт из аэропорта": {"_file": "urgent/first_72_transport.md", "_children": {}},
                "📱 SIM-карта и интернет": {"_file": "urgent/first_72_sim.md", "_children": {}},
                "💸 Деньги в первые дни": {"_file": "urgent/first_72_money.md", "_children": {}},
                "🏠 Первое жильё": {"_file": "urgent/first_72_housing.md", "_children": {}},
                "⚠️ Таиланд — не рай": {"_file": "urgent/thailand_not_paradise.md", "_children": {}},
                "✅ Чек-лист первых 72 часов": {"_file": "urgent/first_day_checklist.md", "_children": {}},
                "❌ Топ-5 ошибок первых дней": {"_file": "urgent/top5_mistakes.md", "_children": {}},
                "🧳 С семьёй и/или питомцем": {"_file": "urgent/family_pets.md", "_children": {}},
            },
        },
        "📄 Визы и легализация": {
            "_file": "visa/intro.md",
            "_children": {
                "🧑‍🎓 ED — учебная виза": {
                    "_file": "visa/ed/intro.md",
                    "_children": {
                        "Кому подходит": {"_file": "visa/ed/who_fits.md", "_children": {}},
                        "Как получить (шаги)": {"_file": "visa/ed/steps.md", "_children": {}},
                        "Риски и ошибки": {"_file": "visa/ed/risks.md", "_children": {}},
                    }
                },
                "🌐 DTV — цифровой кочевник": {
                    "_file": "visa/dtv/intro.md",
                    "_children": {
                        "Кому подходит": {"_file": "visa/dtv/who_fits.md", "_children": {}},
                        "Как получить (шаги)": {"_file": "visa/dtv/steps.md", "_children": {}},
                        "Риски и ошибки": {"_file": "visa/dtv/risks.md", "_children": {}},
                    }
                },
                "💼 Бизнес-виза и работа": {
                    "_file": "visa/business/intro.md",
                    "_children": {
                        "Кому подходит": {"_file": "visa/business/who_fits.md", "_children": {}},
                        "Как получить (шаги)": {"_file": "visa/business/steps.md", "_children": {}},
                        "Риски и ошибки": {"_file": "visa/business/risks.md", "_children": {}},
                    }
                },
                "❤️ Семейная виза": {
                    "_file": "visa/family/intro.md",
                    "_children": {
                        "Основания": {"_file": "visa/family/grounds.md", "_children": {}},
                        "Как получить (шаги)": {"_file": "visa/family/steps.md", "_children": {}},
                        "Риски и ошибки": {"_file": "visa/family/risks.md", "_children": {}},
                    }
                },
                "🧓 Пенсионная виза": {
                    "_file": "visa/retirement/intro.md",
                    "_children": {
                        "Требования": {"_file": "visa/retirement/requirements.md", "_children": {}},
                        "Как получить (шаги)": {"_file": "visa/retirement/steps.md", "_children": {}},
                        "Риски": {"_file": "visa/retirement/risks.md", "_children": {}},
                    }
                },
                "📚 Туристическая виза": {"_file": "visa/tourist.md", "_children": {}},
                "👑 Thailand Elite / Privilege": {"_file": "visa/elite_privilege.md", "_children": {}},
                "⚙️ Продление, TM30, overstay": {
                    "_file": "visa/extensions/intro.md",
                    "_children": {
                        "Где и как продлить": {"_file": "visa/extensions/where_how.md", "_children": {}},
                        "Сроки и штрафы": {"_file": "visa/extensions/deadlines_fines.md", "_children": {}},
                        "Типовые ошибки": {"_file": "visa/extensions/common_mistakes.md", "_children": {}},
                    }
                },
            },
        },
        "💰 Деньги и банки": {
            "_file": "money_home/intro.md",
            "_children": {
                "🏦 Банковский счёт": {"_file": "money_home/bank_account.md", "_children": {}},
                "💱 Обмен валюты": {
                    "_file": "money_home/exchange/intro.md",
                    "_children": {
                        "Где менять выгодно": {"_file": "money_home/exchange/where_best.md", "_children": {}},
                        "Банки vs обменники": {"_file": "money_home/exchange/banks_vs_exchangers.md", "_children": {}},
                        "Безопасность при обмене": {"_file": "money_home/exchange/safety.md", "_children": {}},
                    }
                },
                "💳 Карты и платежи": {
                    "_file": "money_home/payments/intro.md",
                    "_children": {
                        "Нал vs безнал": {"_file": "money_home/payments/cash_vs_cashless.md", "_children": {}},
                        "Карты и блокировки": {"_file": "money_home/payments/cards_blocks.md", "_children": {}},
                        "Что говорить банку": {"_file": "money_home/payments/talk_to_bank.md", "_children": {}},
                    }
                },
                "🏠 Аренда: деньги и договоры": {
                    "_file": "money_home/rent/intro.md",
                    "_children": {
                        "Депозиты и контракты": {"_file": "money_home/rent/deposits_contracts.md", "_children": {}},
                        "Агент ≠ твой друг": {"_file": "money_home/rent/agent_not_friend.md", "_children": {}},
                        "Типовые схемы развода": {"_file": "money_home/rent/scams.md", "_children": {}},
                    }
                },
            },
        },
        "🏠 Жильё и транспорт": {
            "_file": "housing_transport/intro.md",
            "_children": {
                "🏙 Кондо и квартиры": {"_file": "housing_transport/condos.md", "_children": {}},
                "🏡 Дома и виллы": {"_file": "housing_transport/houses_villas.md", "_children": {}},
                "🚗 Автомобили": {"_file": "housing_transport/cars.md", "_children": {}},
                "🛵 Байки и мотоциклы": {"_file": "housing_transport/bikes.md", "_children": {}},
                "⚙️ Полезное по аренде": {"_file": "housing_transport/useful_rent.md", "_children": {}},
            },
        },
        "💬 Как тут жить": {
            "_file": "life/intro.md",
            "_children": {
                "🏥 Медицина и страховка": {"_file": "life/medicine_insurance.md", "_children": {}},
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
        "⚠️ Реальность Таиланда": {
            "_file": "reality/intro.md",
            "_children": {
                "🧠 Ты фаранг — что это значит": {
                    "_file": "reality/farang/intro.md",
                    "_children": {
                        "Что это значит": {"_file": "reality/farang/what_it_means.md", "_children": {}},
                        "Улыбки ≠ дружба": {"_file": "reality/farang/smiles_not_friendship.md", "_children": {}},
                        "Где ошибаются чаще всего": {"_file": "reality/farang/common_errors.md", "_children": {}},
                    }
                },
                "🚩 Помогаторы и мошенники": {
                    "_file": "reality/helpers/intro.md",
                    "_children": {
                        "Красные флаги": {"_file": "reality/helpers/red_flags.md", "_children": {}},
                        "Типовые схемы": {"_file": "reality/helpers/schemes.md", "_children": {}},
                        "Как отказывать": {"_file": "reality/helpers/how_to_say_no.md", "_children": {}},
                    }
                },
                "😵 Типичные ошибки": {
                    "_file": "reality/mistakes/intro.md",
                    "_children": {
                        "Алкоголь и агрессия": {"_file": "reality/mistakes/alcohol_aggression.md", "_children": {}},
                        "Байк и полиция": {"_file": "reality/mistakes/bike_police.md", "_children": {}},
                        "Нелегальная работа": {"_file": "reality/mistakes/illegal_work.md", "_children": {}},
                    }
                },
                "🙏 Культура и запреты": {
                    "_file": "reality/culture/intro.md",
                    "_children": {
                        "Король и религия": {"_file": "reality/culture/king_religion.md", "_children": {}},
                        "Храмы и одежда": {"_file": "reality/culture/temples_clothes.md", "_children": {}},
                        "Потеря лица": {"_file": "reality/culture/lose_face.md", "_children": {}},
                    }
                },
            },
        },
        "🆘 Нужна помощь": {
            "_file": "help/intro.md",
            "_children": {
                "🔍 Разобрать мою ситуацию": {"_file": "help/analyze_my_case.md", "_children": {}},
                "💬 Задать вопрос": {"_file": "help/ask_question.md", "_children": {}},
                "📋 Чек-листы": {
                    "_file": "help/checklists/intro.md",
                    "_children": {
                        "Первый месяц": {"_file": "help/checklists/first_month.md", "_children": {}},
                        "Аренда без потерь": {"_file": "help/checklists/rent_no_losses.md", "_children": {}},
                        "Виза без лишних расходов": {"_file": "help/checklists/visa_no_extra.md", "_children": {}},
                    }
                },
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


# ==================== СТАБИЛЬНАЯ СИСТЕМА ID ====================
def get_stable_node_id(path: List[str]) -> str:
    path_str = ".".join(path)
    return "m" + hashlib.md5(path_str.encode('utf-8')).hexdigest()[:8]


ID_TO_NODE: Dict[str, Dict[str, Any]] = {}
ID_TO_PATH: Dict[str, List[str]] = {}
ID_TO_NAME: Dict[str, str] = {}
PATH_TO_ID: Dict[str, str] = {}


def assign_node_ids(node: Dict[str, Any], current_path: List[str] = None):
    if current_path is None:
        current_path = []

    for name, child in node.get("_children", {}).items():
        new_path = current_path + [name]
        node_id = get_stable_node_id(new_path)

        ID_TO_NODE[node_id] = child
        ID_TO_PATH[node_id] = new_path
        ID_TO_NAME[node_id] = name
        PATH_TO_ID[".".join(new_path)] = node_id

        assign_node_ids(child, new_path)


assign_node_ids(MENU_TREE)

logger.info("=== Stable ID mapping (первые 15) ===")
for i, (nid, pth) in enumerate(list(ID_TO_PATH.items())[:15]):
    logger.info(f"{nid} -> {pth}")
logger.info("=== Конец маппинга ID ===")


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
                InlineKeyboardButton(name, callback_data=f"nav:{CURRENT_MENU_VERSION}:{node_id}")
            ])

    _LEAD_SECTIONS = {
        "📄 Визы и легализация",
        "💰 Деньги и банки",
        "🏠 Жильё и транспорт",
        "💬 Как тут жить",
        "🐾 Животные и переезд",
    }
    in_lead_section = path and path[0] in _LEAD_SECTIONS
    is_leaf = not node.get("_children")
    if in_lead_section and is_leaf:
        topic = path[-1] if path else ""
        buttons.append([
            InlineKeyboardButton(
                "📋 Получить персональный разбор",
                callback_data=f"lead:analyze:{topic[:40]}"
            )
        ])
        buttons.append([
            InlineKeyboardButton(
                "🤝 Передать заявку специалисту",
                callback_data=f"lead:specialist:{topic[:40]}"
            )
        ])
        buttons.append([
            InlineKeyboardButton(
                "⚠️ Сообщить об устаревшей информации",
                callback_data=f"lead:report:{topic[:40]}"
            )
        ])

    important = [
        "📄 Визы и легализация",
        "💰 Деньги и банки",
        "🏠 Жильё и транспорт",
        "💬 Как тут жить",
        "🐾 Животные и переезд",
        "⚠️ Реальность Таиланда",
    ]
    if path and (path[0] in important or any(s in path for s in important)):
        if HELP_ANALYZE_ID:
            buttons.append([
                InlineKeyboardButton("🆘 Разобрать мою ситуацию", callback_data=f"nav:{CURRENT_MENU_VERSION}:{HELP_ANALYZE_ID}")
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
        node = get_node_by_path(path)

        if node is None:
            logger.error(f"INVALID_PATH_IN_SHOW_MENU path={path}")
            context.user_data["path"] = []
            path = []
            node = MENU_TREE

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
                [InlineKeyboardButton(name, callback_data=f"nav:{CURRENT_MENU_VERSION}:{nid}")] 
                for nid, name in favs
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

        if data.startswith("lead:"):
            parts = data.split(":", 2)
            action_type = parts[1] if len(parts) > 1 else "unknown"
            topic = parts[2] if len(parts) > 2 else ""

            _LEAD_MESSAGES = {
                "analyze": "📋 Заявка на персональный разбор принята.\n\nМы передадим её администратору. Как правило, ответ приходит в течение 1–2 рабочих дней.",
                "specialist": "🤝 Заявка на специалиста принята.\n\nМы подберём подходящего специалиста и свяжемся с тобой.",
                "report": "⚠️ Спасибо за сигнал!\n\nМы проверим информацию и обновим её, если она устарела.",
            }
            reply_text = _LEAD_MESSAGES.get(action_type, "Заявка принята.")
            save_lead(user.id, user.username, action_type, topic)
            logger.info(f"LEAD user_id={user.id} username={user.username} action={action_type} topic={topic}")

            admin_id = os.getenv("ADMIN_USER_ID")
            if admin_id:
                try:
                    _LEAD_LABELS = {
                        "analyze": "📋 Персональный разбор",
                        "specialist": "🤝 Заявка на специалиста",
                        "report": "⚠️ Устаревшая информация",
                    }
                    label = _LEAD_LABELS.get(action_type, action_type)
                    admin_text = (
                        f"🔔 Новая заявка\n\n"
                        f"Тип: {label}\n"
                        f"Тема: {topic or '—'}\n"
                        f"Telegram ID: {user.id}\n"
                        f"Username: @{user.username or 'нет'}\n"
                        f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                    )
                    await context.bot.send_message(chat_id=int(admin_id), text=admin_text)
                except Exception as e:
                    logger.error(f"admin notify error: {e}")

            await query.answer(reply_text, show_alert=True)
            return

        if data.startswith("nav:"):
            parts = data.split(":")
            if len(parts) != 3:
                await query.answer("Меню обновилось. Нажмите /start", show_alert=True)
                return

            _, version, node_id = parts

            if version != CURRENT_MENU_VERSION:
                await query.answer("Меню обновилось. Нажмите /start", show_alert=True)
                return

            new_path = ID_TO_PATH.get(node_id)
            logger.info(f"NAV_CLICK node_id={node_id} new_path={new_path}")

            if not new_path:
                await query.answer("Раздел устарел. Нажмите /start", show_alert=True)
                return

            node = get_node_by_path(new_path)
            if node is None:
                logger.error(f"NODE_NOT_FOUND node_id={node_id} path={new_path}")
                await query.answer("Раздел временно недоступен. Нажмите /start", show_alert=True)
                return

            context.user_data["path"] = list(new_path)
            section_name = ID_TO_NAME.get(node_id, new_path[-1])

            try:
                increment_stat(section_name)
                log_user_visit(user.id, user.username, section_name)
            except Exception:
                pass

            await show_menu(update, context)
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
            [InlineKeyboardButton(name, callback_data=f"nav:{CURRENT_MENU_VERSION}:{nid}")] 
            for nid, name in results[:15]
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
            [InlineKeyboardButton(name, callback_data=f"nav:{CURRENT_MENU_VERSION}:{nid}")] 
            for nid, name in favs
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
        [InlineKeyboardButton("📋 Заявки (leads)", callback_data="admin:leads")],
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
    elif data == "admin:leads":
        leads = get_leads(20)
        if leads:
            lines = [f"• @{u or '—'} [{a}] {t} — {c[:16]}" for u, a, t, c in leads]
            text = "📋 Последние заявки\n\n" + "\n".join(lines)
        else:
            text = "📋 Заявок пока нет."
    else:
        text = "Неизвестная команда"

    await update.effective_message.reply_text(text)


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

    logger.info("FarangProBot v6.3 запущен (Render Web Service + Webhook)")

    port = int(os.environ.get("PORT", "10000"))
    webhook_url = os.environ.get("WEBHOOK_URL")

    if not webhook_url:
        raise RuntimeError("WEBHOOK_URL не найден в переменных окружения!")

    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=token,
        webhook_url=f"{webhook_url}/{token}",
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()