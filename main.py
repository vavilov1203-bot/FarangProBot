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
# ДЕРЕВО МЕНЮ (СТРУКТУРА)
# =========================
# Формат узла:
# {
#   "_text": "Текст, который бот пишет при входе в раздел" (опционально),
#   "_children": { "Кнопка": { ...подраздел... }, ... }
# }
MENU_TREE: Dict[str, Any] = {
    "_text": "Выбери пункт из меню 👇",
    "_children": {
        "🏠 Аренда": {
            "_text": "Выбери категорию аренды:",
            "_children": {
                # ПРИМЕРЫ — можешь заменить на свои
                "Квартиры/Кондо": {"_text": "Квартиры/Кондо — сюда добавим гайды и чек-листы.", "_children": {}},
                "Дома": {"_text": "Дома — сюда добавим гайды и чек-листы.", "_children": {}},
                "Договор и депозит": {"_text": "Договор и депозит — важные нюансы.", "_children": {}},
            }
        },

        "🧾 Визы": {
            "_text": "Доступные визы: ED, DTV, Семейная, Бизнес, Пенсионная, Элит и продления штампов.",
            "_children": {
                "ED (учебная)": {"_text": "ED-виза — структура раздела (позже наполним).", "_children": {}},
                "DTV (Digital Nomad)": {"_text": "DTV — условия, документы, подача.", "_children": {}},
                "Семейная": {"_text": "Семейная виза — варианты и требования.", "_children": {}},
                "Бизнес": {"_text": "Бизнес-виза — как легально работать.", "_children": {}},
                "Пенсионная": {"_text": "Пенсионная — требования и продления.", "_children": {}},
                "Элит": {"_text": "Elite — пакеты, цены, нюансы.", "_children": {}},
                "Продление штампов": {"_text": "Продления — сроки, штрафы, лайфхаки.", "_children": {}},
            }
        },

        "💱 Обмен валют": {
            "_text": "Обмен валют — курсы, где менять, безопасность.",
            "_children": {
                "Где выгоднее менять": {"_text": "Где выгоднее — банки/обменники/приложения.", "_children": {}},
                "Безопасность": {"_text": "Как не попасть на подмену/фейки.", "_children": {}},
                "Крипта": {"_text": "Крипта — легальность и риски (общая инфа).", "_children": {}},
            }
        },

        "📸 Фото и видео": {
            "_text": "Фото и видео — услуги, цены, где искать.",
            "_children": {
                "📷 Фотосессии на локациях": {"_text": "Фотосессии — подбор локаций/стиля/цены.", "_children": {}},
                "🎥 Видео туры и дроны": {"_text": "Видео/дроны — условия, разрешения, цены.", "_children": {}},
                "📣 Контент для блогеров": {"_text": "Контент-пакеты для блогеров.", "_children": {}},
            }
        },

        "🌴 Туры и экскурсии": {
            "_text": "Экскурсии по Таиланду: острова, сафари, шоу, храмы — всё под ключ.",
            "_children": {
                "🚗 Однодневные поездки": {
                    "_text": "Однодневные поездки — выбери маршрут:",
                    "_children": {
                        "Паттайя → Бангкок (Mahanakhon, храмы, шопинг)": {
                            "_text": "Маршрут Паттайя → Бангкок (Mahanakhon, храмы, шопинг).",
                            "_children": {}
                        },
                        "Паттайя → Районг (водопады, рынок фруктов)": {
                            "_text": "Маршрут Паттайя → Районг (водопады, рынок фруктов).",
                            "_children": {}
                        },
                        "Паттайя → Кхао Кхео (зоопарк и горы)": {
                            "_text": "Маршрут Паттайя → Кхао Кхео (зоопарк и горы).",
                            "_children": {}
                        },
                    }
                },

                "🏝 Морские туры": {
                    "_text": "Морские туры — выбери:",
                    "_children": {
                        "Ко Лан — острова рядом с Паттайей": {"_text": "Ко Лан — детали тура/цены/советы.", "_children": {}},
                        "Ко Самет — уединённый отдых": {"_text": "Ко Самет — детали тура/цены/советы.", "_children": {}},
                        "Частные лодки и рыбалка": {"_text": "Частные лодки/рыбалка — форматы и цены.", "_children": {}},
                    }
                },

                "🧑‍💼 Гиды и частные туры": {
                    "_text": "Гиды и частные туры — выбери:",
                    "_children": {
                        "Русскоязычные гиды": {"_text": "Русскоязычные гиды — где искать и как выбирать.", "_children": {}},
                        "Тайские гиды (англ / тай)": {"_text": "Тайские гиды — где искать и как выбирать.", "_children": {}},
                        "Персональные маршруты": {"_text": "Персональные маршруты — сбор ТЗ и планирование.", "_children": {}},
                    }
                },

                "✨ Необычные места": {
                    "_text": "Необычные места — выбери:",
                    "_children": {
                        "Храмы вне туристических маршрутов": {"_text": "Нетуристические храмы — подборки.", "_children": {}},
                        "Кофейни с атмосферой": {"_text": "Кофейни — подборки и районы.", "_children": {}},
                        "Ночные рынки и деревни": {"_text": "Ночные рынки/деревни — куда ехать.", "_children": {}},
                    }
                },
            }
        },

        "🛡️ Страховки": {
            "_text": "Страховки — здоровье, путешествия, авто/байк, имущество.",
            "_children": {
                "Медицинская": {"_text": "Медицинская страховка — как выбрать.", "_children": {}},
                "Путешествия": {"_text": "Travel страховка — нюансы.", "_children": {}},
                "Авто/байк": {"_text": "Авто/байк страховка — что покрывает.", "_children": {}},
            }
        },

        "⚠️ Поведение и культура": {
            "_text": "Поведение и культура — что важно знать в Таиланде.",
            "_children": {
               "{ } Прежде чем ты начнёшь": {
                   "_text": load_content(content_path("behavior/before_you_start.md")),
                   "_children": {}
            },
                    "🙏 Тайская культура и табу": {
                "_text": load_content(content_path("taboo/intro.md")),
                "_children": {
                    "👑 Король, религия и «святые» темы": {
                        "_text": load_content(content_path("taboo/king_religion.md")),
                        "_children": {}
                    },
                    "⛩️ Как вести себя в храме": {
                        "_text": load_content(content_path("taboo/temple_rules.md")),
                        "_children": {}
                    },
                    "👣 Голова, ноги, касания": {
                        "_text": load_content(content_path("taboo/head_feet_touch.md")),
                        "_children": {}
                    },
                    "👕 Одежда и нормы": {
                        "_text": load_content(content_path("taboo/clothes_public_norms.md")),
                        "_children": {}
                    },
                }
            },
                            "🙂 Типичные ошибки фарангов": {
                "_text": load_content(content_path("mistakes/intro.md")),
                "_children": {
                    "💸 Я заплатил — значит, можно": {
                        "_text": load_content(content_path("mistakes/i_paid_so_i_can.md")),
                        "_children": {}
                    },
                    "😡 Агрессия и алкоголь": {
                        "_text": load_content(content_path("mistakes/aggression_alcohol.md")),
                        "_children": {}
                    },
                    "🍻 Тайки, бары и чувство меры": {
                        "_text": load_content(content_path("mistakes/bars_and_boundaries.md")),
                        "_children": {}
                    },
                    "🏍 Нелегальная работа, мотоциклы без прав": {
                        "_text": load_content(content_path("mistakes/illegal_work_and_bike.md")),
                        "_children": {}
                    }
                }
            },

                "💡 Как вызывать уважение": {
                    "_text": "Как вызывать уважение — выбери:",
                    "_children": {
                        "Вежливость — не слабость": {"_text": "Вежливость — не слабость.", "_children": {}},
                        "Сохранять лицо даже в споре": {"_text": "Сохранять лицо — ключ.", "_children": {}},
                        "Слушать, а не доказывать": {"_text": "Слушать, а не доказывать.", "_children": {}},
                        "Простые фразы, которые помогают": {"_text": "Фразы: (позже добавим список).", "_children": {}},
                    }
                },

                "🧘‍♂️ Сабай-сабай — философия спокойствия": {
                    "_text": "Сабай-сабай — выбери:",
                    "_children": {
                        "Что значит “сабай” и “санук”": {"_text": "Сабай/санук — смысл.", "_children": {}},
                        "Почему тайцы не спешат": {"_text": "Почему не спешат — культурно.", "_children": {}},
                        "Как не бороться с хаосом, а жить в нём": {"_text": "Как жить в хаосе — практично.", "_children": {}},
                        "Как сохранить внутренний баланс в чужой стране": {"_text": "Баланс — опоры и рутина.", "_children": {}},
                    }
                },
            }
        },

        "🐾 Животные и переезд": {
            "_text": "Животные и переезд — выбери раздел:",
            "_children": {
                "✈️ Ввоз питомца в Таиланд": {
                    "_text": "Ввоз питомца в Таиланд — выбери тему:",
                    "_children": {
                        "Правила и документы": {"_text": "Правила и документы.", "_children": {}},
                        "Разрешённые виды животных": {"_text": "Разрешённые виды животных.", "_children": {}},
                        "Справки, микрочип и прививки": {"_text": "Справки/микрочип/прививки.", "_children": {}},
                        "Полёт и авиаперевозка": {"_text": "Полёт/перевозка — варианты.", "_children": {}},
                        "Таможня и получение в аэропорту": {"_text": "Таможня/получение в аэропорту.", "_children": {}},
                    }
                },

                "📄 Документы и требования": {
                    "_text": "Документы и требования — выбери тему:",
                    "_children": {
                        "Формы и сертификаты (Vet Health Certificate, Export Permit)": {
                            "_text": "Формы и сертификаты — список и примеры.",
                            "_children": {}
                        },
                        "Где получить разрешение в DLD (Department of Livestock Development)": {
                            "_text": "DLD — куда идти и что делать.",
                            "_children": {}
                        },
                        "Сроки действия справок": {"_text": "Сроки действия справок.", "_children": {}},
                        "Примеры заполнения": {"_text": "Примеры заполнения.", "_children": {}},
                    }
                },

                "🏥 Ветеринария и уход": {
                    "_text": "Ветеринария и уход — выбери:",
                    "_children": {
                        "Ветклиники и госпитали (Бангкок, Паттайя, Чиангмай)": {
                            "_text": "Ветклиники/госпитали — список (позже наполним).",
                            "_children": {}
                        },
                        "Вакцинация, анализы, чипирование": {"_text": "Вакцинация/анализы/чип.", "_children": {}},
                        "Страховка для животных": {"_text": "Страховка для животных.", "_children": {}},
                        "Груминг, передержка, передвижение по стране": {"_text": "Груминг/передержка/по стране.", "_children": {}},
                        "Вакцины, которых требуют в Таиланде": {"_text": "Требуемые вакцины.", "_children": {}},
                    }
                },

                "🌍 Вывоз из Таиланда": {
                    "_text": "Вывоз из Таиланда — выбери:",
                    "_children": {
                        "Документы для вывоза в другие страны": {"_text": "Документы для вывоза.", "_children": {}},
                        "Справки в DLD и сертификаты здоровья": {"_text": "DLD справки и сертификаты.", "_children": {}},
                        "Перелёт и транспортные контейнеры": {"_text": "Контейнеры/переноски/перелёт.", "_children": {}},
                        "Примеры маршрутов (в Россию, Европу, Латинскую Америку)": {"_text": "Маршруты — примеры.", "_children": {}},
                    }
                },

                "🐈 Практические советы": {
                    "_text": "Практические советы — выбери:",
                    "_children": {
                        "Как найти жильё с животным": {"_text": "Жильё с животным — как искать.", "_children": {}},
                        "Как подготовить кота или собаку к полёту": {"_text": "Подготовка к полёту.", "_children": {}},
                        "Что нельзя ввозить": {"_text": "Что нельзя ввозить.", "_children": {}},
                        "Как снизить стресс у животного": {"_text": "Как снизить стресс.", "_children": {}},
                        "Реальные истории переезда": {"_text": "Истории — добавим позже.", "_children": {}},
                    }
                },
            }
        },

        "💼 Работа и налоги": {
            "_text": "Работа и налоги — выбери тему:",
            "_children": {
                "Digital Nomad и удалёнка": {"_text": "Удалёнка/номад — что важно знать.", "_children": {}},
                "Налоговое резидентство (180 дней и декларации)": {"_text": "Резидентство (180 дней, декларации).", "_children": {}},
                "Крипта и фриланс в Таиланде": {"_text": "Крипта/фриланс — общие правила и риски.", "_children": {}},
                "Как не попасть под нелегальную деятельность": {"_text": "Как не попасть под нелегал.", "_children": {}},
                "Налоги, если живёшь долго": {"_text": "Налоги при долгом проживании.", "_children": {}},
            }
        },

        "🧰 Советы по быту и сервисы для дома": {
            "_text": "Быт и сервисы — подборки (добавим позже).",
            "_children": {}
        },
    }
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
    buttons = list(node.get("_children", {}).keys())

    rows = []
    for b in buttons:
        rows.append([b])  # по 1 кнопке в строке (как на твоих скринах)

    # навигация
    nav_row = []
    if not is_root:
        nav_row.append(BTN_BACK)
        nav_row.append(BTN_HOME)
        rows.append(nav_row)

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
        path.append(txt)
        context.user_data["path"] = path
        await show_menu(update, context)
        return

    # если текст не кнопка
    await update.message.reply_text("Выбери пункт кнопкой 👇")

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
