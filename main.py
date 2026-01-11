import os
from typing import Dict, Any, List, Optional

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# =========================
# Настройки
# =========================

BOT_NAME = "FarangProBot"

BTN_BACK = "⬅️ Назад"
BTN_HOME = "🏠 Главное меню"

# =========================
# Дерево меню (структура)
# =========================
# Узел:
# {
#   "title": "Текст кнопки",
#   "children": [child_id, ...]  # если это меню
#   "text": "Ответ"              # если это лист (контент)
# }

NODES: Dict[str, Dict[str, Any]] = {
    # --- Корень ---
    "root": {
        "title": "root",
        "children": [
            "home_tips",
            "work_taxes",
            "pets_relocation",
            "culture",
            "excursions_guides",
            "photo_video",
        ],
    },

    # =========================
    # Советы по быту и сервисы
    # =========================
    "home_tips": {
        "title": "🏠 Советы по быту и сервисы для дома",
        "text": "Раздел в разработке. Сюда добавим: доставка, связи/интернет, медицина, банки, сервисы, бытовые лайфхаки.",
    },

    # =========================
    # Работа и налоги
    # =========================
    "work_taxes": {
        "title": "💼 Работа и налоги",
        "children": [
            "work_dn",
            "work_tax_resident",
            "work_crypto_freelance",
            "work_illegal",
            "work_long_term_taxes",
        ],
    },
    "work_dn": {
        "title": "🌍 Digital Nomad и удалёнка",
        "text": "Заглушка: правила для удалёнки, счета, платежи, риски, как безопаснее жить и работать.",
    },
    "work_tax_resident": {
        "title": "🧾 Налоговое резидентство (180 дней и декларации)",
        "text": "Заглушка: резидентство, 180 дней, когда возникают обязательства, какие документы вести.",
    },
    "work_crypto_freelance": {
        "title": "🪙 Крипта и фриланс в Таиланде",
        "text": "Заглушка: общие принципы, риски, что точно нельзя, как не светиться лишний раз.",
    },
    "work_illegal": {
        "title": "⚠️ Как не попасть под нелегальную деятельность",
        "text": "Заглушка: типовые ошибки фарангов, что считается работой, чего избегать.",
    },
    "work_long_term_taxes": {
        "title": "📌 Налоги, если живёшь долго",
        "text": "Заглушка: долгий срок, что учитывать, какие вопросы задавать юристу/бухгалтеру.",
    },

    # =========================
    # Животные и переезд
    # =========================
    "pets_relocation": {
        "title": "🐾 Животные и переезд",
        "children": [
            "pets_import_th",
            "pets_docs",
            "pets_vet_care",
            "pets_export_th",
            "pets_practical",
        ],
    },

    # Ввоз питомца в Таиланд
    "pets_import_th": {
        "title": "✈️ Ввоз питомца в Таиланд",
        "children": [
            "pets_import_rules",
            "pets_import_allowed",
            "pets_import_vaccines",
            "pets_import_flight",
            "pets_import_customs",
        ],
    },
    "pets_import_rules": {"title": "📄 Правила и документы", "text": "Заглушка: какие документы нужны, общий порядок действий."},
    "pets_import_allowed": {"title": "✅ Разрешённые виды животных", "text": "Заглушка: какие животные допускаются, ограничения."},
    "pets_import_vaccines": {"title": "💉 Справки, микрочип и прививки", "text": "Заглушка: чип, вакцинации, сроки, что проверяют."},
    "pets_import_flight": {"title": "🛫 Полёт и авиаперевозка", "text": "Заглушка: карго/в салоне, переноска, требования авиакомпаний."},
    "pets_import_customs": {"title": "🛃 Таможня и получение в аэропорту", "text": "Заглушка: где получать, какие кабинеты/службы, типовые вопросы."},

    # Документы и требования
    "pets_docs": {
        "title": "📑 Документы и требования",
        "children": [
            "pets_docs_forms",
            "pets_docs_dld",
            "pets_docs_terms",
            "pets_docs_examples",
        ],
    },
    "pets_docs_forms": {
        "title": "🧾 Формы и сертификаты (Vet Health Certificate, Export Permit)",
        "text": "Заглушка: какие формы бывают, где берутся, кто заполняет.",
    },
    "pets_docs_dld": {
        "title": "🏛️ Где получить разрешение в DLD (Department of Livestock Development)",
        "text": "Заглушка: DLD, куда обращаться, что подготовить.",
    },
    "pets_docs_terms": {"title": "⏳ Сроки действия справок", "text": "Заглушка: сроки, почему важно попасть в окно дат."},
    "pets_docs_examples": {"title": "📝 Примеры заполнения", "text": "Заглушка: примеры/шаблоны заполнения."},

    # Ветеринария и уход
    "pets_vet_care": {
        "title": "🏥 Ветеринария и уход",
        "children": [
            "pets_vet_clinics",
            "pets_vet_vaccines",
            "pets_vet_insurance",
            "pets_vet_grooming",
            "pets_vet_required",
        ],
    },
    "pets_vet_clinics": {"title": "🏥 Ветклиники и госпитали (Бангкок, Паттайя, Чиангмай)", "text": "Заглушка: список/критерии выбора клиники."},
    "pets_vet_vaccines": {"title": "💉 Вакцинация, анализы, чипирование", "text": "Заглушка: базовый чек-лист."},
    "pets_vet_insurance": {"title": "🛡️ Страховка для животных", "text": "Заглушка: опции, что покрывают/не покрывают."},
    "pets_vet_grooming": {"title": "✂️ Груминг, передержка, передвижение по стране", "text": "Заглушка: груминг/передержка, правила перевозки."},
    "pets_vet_required": {"title": "📌 Вакцины, которых требуют в Таиланде", "text": "Заглушка: какие прививки обычно проверяют."},

    # Вывоз из Таиланда
    "pets_export_th": {
        "title": "🌍 Вывоз из Таиланда",
        "children": [
            "pets_export_docs",
            "pets_export_dld",
            "pets_export_flight",
            "pets_export_routes",
        ],
    },
    "pets_export_docs": {"title": "📄 Документы для вывоза в другие страны", "text": "Заглушка: общий список документов под страны."},
    "pets_export_dld": {"title": "🏛️ Справки в DLD и сертификаты здоровья", "text": "Заглушка: как получать и где."},
    "pets_export_flight": {"title": "🧳 Перелёт и транспортные контейнеры", "text": "Заглушка: контейнер, требования IATA, размеры."},
    "pets_export_routes": {"title": "🗺️ Примеры маршрутов (в Россию, Европу, Латинскую Америку)", "text": "Заглушка: примеры логики маршрутов."},

    # Практические советы
    "pets_practical": {
        "title": "🐕 Практические советы",
        "children": [
            "pets_practical_housing",
            "pets_practical_prepare",
            "pets_practical_forbidden",
            "pets_practical_stress",
            "pets_practical_stories",
        ],
    },
    "pets_practical_housing": {"title": "🏠 Как найти жильё с животным", "text": "Заглушка: как спрашивать, что писать хозяину, депозит."},
    "pets_practical_prepare": {"title": "🧰 Как подготовить кота или собаку к полёту", "text": "Заглушка: переноска, привычка, вода/еда, спокойствие."},
    "pets_practical_forbidden": {"title": "🚫 Что нельзя ввозить", "text": "Заглушка: типовые ограничения."},
    "pets_practical_stress": {"title": "🧘 Как снизить стресс у животного", "text": "Заглушка: адаптация, режим, переноска, безопасные методы."},
    "pets_practical_stories": {"title": "📖 Реальные истории переезда", "text": "Заглушка: истории/кейсы."},

    # =========================
    # Поведение и культура
    # =========================
    "culture": {
        "title": "⚠️ Поведение и культура",
        "children": [
            "culture_before",
            "culture_taboos",
            "culture_mistakes",
            "culture_respect",
            "culture_sabai",
        ],
    },

    "culture_before": {
        "title": "{ } Прежде чем ты начнёшь",
        "children": [
            "culture_before_nobody_waits",
            "culture_before_respect_currency",
            "culture_before_smile_not_friend",
        ],
    },
    "culture_before_nobody_waits": {"title": "🧩 Никто не ждёт — но и не мешает", "text": "Заглушка: как устроено отношение к фарангам и почему это нормально."},
    "culture_before_respect_currency": {"title": "💠 Уважение как валюта", "text": "Заглушка: почему уважение важнее правоты."},
    "culture_before_smile_not_friend": {"title": "🙂 Почему “улыбка” не значит “друг”", "text": "Заглушка: улыбка как социальная маска, не обещание близости."},

    "culture_taboos": {
        "title": "🙏 Тайская культура и табу",
        "children": [
            "culture_taboos_king_religion",
            "culture_taboos_temple",
            "culture_taboos_gestures",
            "culture_taboos_clothes",
        ],
    },
    "culture_taboos_king_religion": {"title": "👑 Король, религия и “святые” темы", "text": "Заглушка: что нельзя обсуждать/шутить и почему."},
    "culture_taboos_temple": {"title": "🏯 Как вести себя в храме", "text": "Заглушка: обувь, одежда, фото, тишина, уважение."},
    "culture_taboos_gestures": {"title": "🚫 Что нельзя делать (жесты, касания, ноги, голова)", "text": "Заглушка: голова/ноги/касания/указания."},
    "culture_taboos_clothes": {"title": "👕 Одежда, интим, общественные нормы", "text": "Заглушка: что считается нормой в публичных местах."},

    "culture_mistakes": {
        "title": "😬 Типичные ошибки фарангов",
        "children": [
            "culture_mistakes_paid",
            "culture_mistakes_agression_alcohol",
            "culture_mistakes_girls_bars",
            "culture_mistakes_illegal",
        ],
    },
    "culture_mistakes_paid": {"title": "💸 “Я заплатил — значит, можно”", "text": "Заглушка: почему это часто ломает отношения и сервис."},
    "culture_mistakes_agression_alcohol": {"title": "🍺 Агрессия и алкоголь", "text": "Заглушка: типовые сценарии проблем и как не попасть."},
    "culture_mistakes_girls_bars": {"title": "🍸 Тайки, бары и чувство меры", "text": "Заглушка: осторожность, ожидания, деньги, границы."},
    "culture_mistakes_illegal": {"title": "⚠️ Нелегальная работа, мотоциклы без прав", "text": "Заглушка: риски, штрафы, последствия."},

    "culture_respect": {
        "title": "💡 Как вызывать уважение",
        "children": [
            "culture_respect_polite",
            "culture_respect_face",
            "culture_respect_listen",
            "culture_respect_phrases",
        ],
    },
    "culture_respect_polite": {"title": "🤝 Вежливость — не слабость", "text": "Заглушка: почему мягкость даёт результат."},
    "culture_respect_face": {"title": "😌 Сохранять лицо даже в споре", "text": "Заглушка: как спорить, не унижая собеседника."},
    "culture_respect_listen": {"title": "👂 Слушать, а не доказывать", "text": "Заглушка: как получить “да” без давления."},
    "culture_respect_phrases": {"title": "🗣️ Простые фразы, которые помогают (“коп кун кхрап”, “май пен рай”)", "text": "Заглушка: мини-набор фраз + когда их говорить."},

    "culture_sabai": {
        "title": "🧘 Сабай-сабай — философия спокойствия",
        "children": [
            "culture_sabai_meaning",
            "culture_sabai_not_rush",
            "culture_sabai_chaos",
            "culture_sabai_balance",
        ],
    },
    "culture_sabai_meaning": {"title": "🧩 Что значит “сабай” и “санук”", "text": "Заглушка: смысл слов и как это влияет на быт."},
    "culture_sabai_not_rush": {"title": "🐢 Почему тайцы не спешат", "text": "Заглушка: другой ритм, другое отношение ко времени."},
    "culture_sabai_chaos": {"title": "🌊 Как не бороться с хаосом, а жить в нём", "text": "Заглушка: адаптация, ожидания, гибкость."},
    "culture_sabai_balance": {"title": "⚖️ Как сохранить внутренний баланс в чужой стране", "text": "Заглушка: психогигиена, режим, опоры."},

    # =========================
    # Экскурсии и гиды
    # =========================
    "excursions_guides": {
        "title": "🌴 Экскурсии и гиды",
        "children": [
            "exc_daytrips",
            "exc_sea",
            "exc_private_guides",
            "exc_unusual",
        ],
    },

    "exc_daytrips": {
        "title": "🚗 Однодневные поездки",
        "children": [
            "exc_daytrip_bkk",
            "exc_daytrip_rayong",
            "exc_daytrip_khaokheo",
        ],
    },
    "exc_daytrip_bkk": {"title": "🏙️ Паттайя → Бангкок (Mahanakhon, храмы, шопинг)", "text": "Заглушка: маршрут/время/бюджет/советы."},
    "exc_daytrip_rayong": {"title": "🌿 Паттайя → Районг (водопады, рынок фруктов)", "text": "Заглушка: куда заехать, что попробовать."},
    "exc_daytrip_khaokheo": {"title": "🦒 Паттайя → Khao Kheo (зоопарк и горы)", "text": "Заглушка: лучший время, билеты, лайфхаки."},

    "exc_sea": {
        "title": "🏝️ Морские туры",
        "children": [
            "exc_sea_kolan",
            "exc_sea_kosamet",
            "exc_sea_private_boat",
        ],
    },
    "exc_sea_kolan": {"title": "🌊 Ко Лан — острова рядом с Паттайей", "text": "Заглушка: пляжи, как добраться, цены."},
    "exc_sea_kosamet": {"title": "🏖️ Ко Самет — уединённый отдых", "text": "Заглушка: где жить, что делать, советы."},
    "exc_sea_private_boat": {"title": "⛵ Частные лодки и рыбалка", "text": "Заглушка: аренда, безопасность, что уточнять."},

    "exc_private_guides": {
        "title": "🧑‍💼 Гиды и частные туры",
        "children": [
            "exc_guides_ru",
            "exc_guides_th",
            "exc_guides_routes",
            "exc_guides_photo_content",
        ],
    },
    "exc_guides_ru": {"title": "🇷🇺 Русскоязычные гиды", "text": "Заглушка: как выбирать, вопросы перед бронированием."},
    "exc_guides_th": {"title": "🇹🇭 Тайские гиды (англ/тай)", "text": "Заглушка: как договориться, что уточнять."},
    "exc_guides_routes": {"title": "🗺️ Персональные маршруты", "text": "Заглушка: маршрут под тебя: интересы/время/бюджет."},
    "exc_guides_photo_content": {"title": "📸 Контент для блогеров", "text": "Заглушка: локации/тайминг/свет/сценарий."},

    "exc_unusual": {
        "title": "✨ Необычные места",
        "children": [
            "exc_unusual_temples",
            "exc_unusual_coffee",
            "exc_unusual_night",
        ],
    },
    "exc_unusual_temples": {"title": "🏯 Храмы вне туристических маршрутов", "text": "Заглушка: идеи и правила поведения."},
    "exc_unusual_coffee": {"title": "☕ Кофейни с атмосферой", "text": "Заглушка: подборка формата."},
    "exc_unusual_night": {"title": "🌙 Ночные рынки и деревни", "text": "Заглушка: что смотреть, безопасность."},

    # =========================
    # Фото и видео сопровождение (как на скрине — отдельным пунктом снизу)
    # =========================
    "photo_video": {
        "title": "📷 Фото и видео сопровождение",
        "children": [
            "pv_photosession",
            "pv_video_drone",
            "pv_bloggers",
        ],
    },
    "pv_photosession": {"title": "📸 Фотосессии на локациях", "text": "Заглушка: форматы, как подготовиться, что уточнить."},
    "pv_video_drone": {"title": "🎥 Видео туры и дроны", "text": "Заглушка: что можно/нельзя, разрешения, безопасность."},
    "pv_bloggers": {"title": "📣 Контент для блогеров", "text": "Заглушка: идеи, сценарии, локации."},
}


# =========================
# Вспомогательные функции
# =========================

def node_title(node_id: str) -> str:
    return NODES[node_id]["title"]

def get_children(node_id: str) -> List[str]:
    return NODES[node_id].get("children", [])

def is_menu(node_id: str) -> bool:
    return "children" in NODES[node_id]

def get_text(node_id: str) -> str:
    return NODES[node_id].get("text", "Раздел в разработке.")

def build_keyboard(node_id: str) -> ReplyKeyboardMarkup:
    """
    Строит клавиатуру для текущего меню.
    Автоматически добавляет Назад и Главное меню.
    """
    children = get_children(node_id)

    # Кнопки детей: по 1 в строке (как у тебя на скринах-структуре)
    rows = [[node_title(ch)] for ch in children]

    # Навигация
    nav_row = []
    if node_id != "root":
        nav_row.append(BTN_BACK)
        nav_row.append(BTN_HOME)
    if nav_row:
        rows.append(nav_row)

    return ReplyKeyboardMarkup(rows, resize_keyboard=True)

def find_node_by_title(current_menu_id: str, title: str) -> Optional[str]:
    """
    Ищет дочерний узел по названию кнопки (title) внутри текущего меню.
    """
    for ch in get_children(current_menu_id):
        if node_title(ch) == title:
            return ch
    return None

def get_path(context: ContextTypes.DEFAULT_TYPE) -> List[str]:
    """
    Путь меню: список node_id, например ["root", "culture", "culture_taboos"]
    """
    path = context.user_data.get("path")
    if not path:
        path = ["root"]
        context.user_data["path"] = path
    return path


# =========================
# Хендлеры
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["path"] = ["root"]
    kb = build_keyboard("root")
    await update.message.reply_text(
        f"Привет 👋 Я {BOT_NAME}!\nВыбери нужный раздел ⤵️",
        reply_markup=kb
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    path = get_path(context)
    current_menu = path[-1]

    # --- Навигация ---
    if text == BTN_HOME:
        context.user_data["path"] = ["root"]
        kb = build_keyboard("root")
        await update.message.reply_text("Главное меню:", reply_markup=kb)
        return

    if text == BTN_BACK:
        if len(path) > 1:
            path.pop()
        current_menu = path[-1]
        kb = build_keyboard(current_menu)
        await update.message.reply_text("Назад:", reply_markup=kb)
        return

    # --- Переход по дереву ---
    # 1) Пытаемся найти выбранную кнопку среди детей текущего меню
    target = find_node_by_title(current_menu, text)

    if target is None:
        # Нажали не то / написали руками
        kb = build_keyboard(current_menu)
        await update.message.reply_text("Выбери пункт из меню ⤵️", reply_markup=kb)
        return

    # 2) Если это меню — открываем его
    if is_menu(target):
        path.append(target)
        kb = build_keyboard(target)
        await update.message.reply_text(node_title(target), reply_markup=kb)
        return

    # 3) Если это лист — показываем текст (и оставляем клаву текущего меню)
    kb = build_keyboard(current_menu)
    await update.message.reply_text(get_text(target), reply_markup=kb)


def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("❌ Ошибка: не найден TELEGRAM_BOT_TOKEN")
        return

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
