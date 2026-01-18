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
                        "⚠️ Таиланд — не рай. Прочитай в первый день": {
                            "_text": load_content(content_path("situations/thailand_not_paradise.md")),
                            "_children": {},
                        },
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
                                "➡️ Открыть основной раздел: 🧰 Советы по быту и сервисы": {
                                    "_goto": ["🧰 Советы по быту и сервисы"]
                                },
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
                                "➡️ Открыть основной раздел: ⚠️ Поведение и культура": {
                                    "_goto": ["⚠️ Поведение и культура"]
                                },
                            },
                        },
                    },
                },

                # -------------------------
                # 👨‍👩‍👦 Я с семьёй / ребёнок  (СКРЫТО ДЛЯ ПОЛЬЗОВАТЕЛЕЙ)
                # -------------------------
                "👨‍👩‍👦 Я с семьёй / ребёнок": {
                    "_disabled": True,
                    "_text": load_content(content_path("situations/with_family.md")),
                    "_children": {
                        "🏠 Жильё для семьи — как выбирать": {
                            "_text": load_content(content_path("situations/family_rent.md")),
                            "_children": {
                                "➡️ Открыть основной раздел: 🧰 Советы по быту и сервисы": {
                                    "_goto": ["🧰 Советы по быту и сервисы"]
                                },
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
                                "➡️ Открыть основной раздел: 🧰 Советы по быту и сервисы": {
                                    "_goto": ["🧰 Советы по быту и сервисы"]
                                },
                            },
                        },
                        "⚠️ Культура — чтобы не было проблем у семьи": {
                            "_text": load_content(content_path("situations/family_culture.md")),
                            "_children": {
                                "➡️ Открыть основной раздел: ⚠️ Поведение и культура": {
                                    "_goto": ["⚠️ Поведение и культура"]
                                },
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
                    "_text": load_content(content_path("exchange/intro.md")),
                    "_children": {
                        "Где выгоднее менять": {
                            "_text": load_content(content_path("exchange/where_best.md")),
                            "_children": {
                                "Банки vs обменники": {"_text": load_content(content_path("exchange/banks_vs_exchangers.md")), "_children": {}},
                                "Курс, комиссии, спред": {"_text": load_content(content_path("exchange/rates_fees_spread.md")), "_children": {}},
                                "Как сравнивать курсы быстро": {"_text": load_content(content_path("exchange/how_to_compare.md")), "_children": {}},
                            },
                        },
                        "Безопасность": {
                            "_text": load_content(content_path("exchange/safety.md")),
                            "_children": {
                                "Подмена купюр / фейки": {"_text": load_content(content_path("exchange/fake_notes.md")), "_children": {}},
                                "Как выбирать обменник": {"_text": load_content(content_path("exchange/how_choose_exchange.md")), "_children": {}},
                                "Большие суммы": {"_text": load_content(content_path("exchange/large_amounts.md")), "_children": {}},
                            },
                        },
                        "Крипта": {
                            "_text": load_content(content_path("exchange/crypto_intro.md")),
                            "_children": {
                                "P2P: базовые правила": {"_text": load_content(content_path("exchange/p2p_rules.md")), "_children": {}},
                                "Риски блокировок": {"_text": load_content(content_path("exchange/blocks_risks.md")), "_children": {}},
                                "Что говорить/не говорить банку": {"_text": load_content(content_path("exchange/bank_questions.md")), "_children": {}},
                            },
                        },
                    },
                },
            },
        },

        # ==========================================================
        # ✅ 2) 📄 ВИЗЫ
        # ==========================================================
        "📄 Визы": {
            "_text": load_content(content_path("visas/intro.md")),
            "_children": {
                "ED (учебная)": {
                    "_text": load_content(content_path("visas/ed/intro.md")),
                    "_children": {
                        "Кому подходит": {"_text": load_content(content_path("visas/ed/who_fits.md")), "_children": {}},
                        "Документы": {"_text": load_content(content_path("visas/ed/docs.md")), "_children": {}},
                        "Пошагово: оформление": {"_text": load_content(content_path("visas/ed/steps.md")), "_children": {}},
                        "Сроки и продления": {"_text": load_content(content_path("visas/ed/extensions.md")), "_children": {}},
                        "Сколько стоит": {"_text": load_content(content_path("visas/ed/cost.md")), "_children": {}},
                        "Риски и ошибки": {"_text": load_content(content_path("visas/ed/risks.md")), "_children": {}},
                    },
                },
                "DTV (Digital Nomad)": {
                    "_text": load_content(content_path("visas/dtv/intro.md")),
                    "_children": {
                        "Кому подходит": {"_text": load_content(content_path("visas/dtv/who_fits.md")), "_children": {}},
                        "Документы": {"_text": load_content(content_path("visas/dtv/docs.md")), "_children": {}},
                        "Пошагово: подача": {"_text": load_content(content_path("visas/dtv/steps.md")), "_children": {}},
                        "Сроки и продления": {"_text": load_content(content_path("visas/dtv/extensions.md")), "_children": {}},
                        "Сколько стоит": {"_text": load_content(content_path("visas/dtv/cost.md")), "_children": {}},
                        "Риски и ошибки": {"_text": load_content(content_path("visas/dtv/risks.md")), "_children": {}},
                    },
                },
                "Семейная": {
                    "_text": load_content(content_path("visas/family/intro.md")),
                    "_children": {
                        "Варианты семейных оснований": {"_text": load_content(content_path("visas/family/options.md")), "_children": {}},
                        "Документы": {"_text": load_content(content_path("visas/family/docs.md")), "_children": {}},
                        "Пошагово: оформление": {"_text": load_content(content_path("visas/family/steps.md")), "_children": {}},
                        "Сроки и продления": {"_text": load_content(content_path("visas/family/extensions.md")), "_children": {}},
                        "Сколько стоит": {"_text": load_content(content_path("visas/family/cost.md")), "_children": {}},
                        "Риски и ошибки": {"_text": load_content(content_path("visas/family/risks.md")), "_children": {}},
                    },
                },
                "Бизнес": {
                    "_text": load_content(content_path("visas/business/intro.md")),
                    "_children": {
                        "Кому подходит": {"_text": load_content(content_path("visas/business/who_fits.md")), "_children": {}},
                        "Документы": {"_text": load_content(content_path("visas/business/docs.md")), "_children": {}},
                        "Пошагово: оформление": {"_text": load_content(content_path("visas/business/steps.md")), "_children": {}},
                        "Work Permit: базовая логика": {"_text": load_content(content_path("visas/business/work_permit_basics.md")), "_children": {}},
                        "Сколько стоит": {"_text": load_content(content_path("visas/business/cost.md")), "_children": {}},
                        "Риски и ошибки": {"_text": load_content(content_path("visas/business/risks.md")), "_children": {}},
                    },
                },
                "Пенсионная": {
                    "_text": load_content(content_path("visas/retirement/intro.md")),
                    "_children": {
                        "Кому подходит": {"_text": load_content(content_path("visas/retirement/who_fits.md")), "_children": {}},
                        "Финансовые требования": {"_text": load_content(content_path("visas/retirement/finance.md")), "_children": {}},
                        "Документы": {"_text": load_content(content_path("visas/retirement/docs.md")), "_children": {}},
                        "Пошагово: оформление": {"_text": load_content(content_path("visas/retirement/steps.md")), "_children": {}},
                        "Продления": {"_text": load_content(content_path("visas/retirement/extensions.md")), "_children": {}},
                        "Риски и ошибки": {"_text": load_content(content_path("visas/retirement/risks.md")), "_children": {}},
                    },
                },
                "Элит": {
                    "_text": load_content(content_path("visas/elite/intro.md")),
                    "_children": {
                        "Пакеты и отличия": {"_text": load_content(content_path("visas/elite/packages.md")), "_children": {}},
                        "Что реально даёт": {"_text": load_content(content_path("visas/elite/benefits.md")), "_children": {}},
                        "Сколько стоит": {"_text": load_content(content_path("visas/elite/cost.md")), "_children": {}},
                        "Риски и ограничения": {"_text": load_content(content_path("visas/elite/risks.md")), "_children": {}},
                    },
                },
                "Продление штампов": {
                    "_text": load_content(content_path("visas/extensions/intro.md")),
                    "_children": {
                        "Где продлевать": {"_text": load_content(content_path("visas/extensions/where.md")), "_children": {}},
                        "Какие документы": {"_text": load_content(content_path("visas/extensions/docs.md")), "_children": {}},
                        "Сроки и штрафы": {"_text": load_content(content_path("visas/extensions/deadlines_fines.md")), "_children": {}},
                        "Типовые ошибки": {"_text": load_content(content_path("visas/extensions/mistakes.md")), "_children": {}},
                    },
                },
            },
        },

        # ==========================================================
        # ✅ 3) 🛡️ СТРАХОВКИ
        # ==========================================================
        "🛡️ Страховки": {
            "_text": load_content(content_path("insurance/intro.md")),
            "_children": {
                "Медицинская": {
                    "_text": load_content(content_path("insurance/medical/intro.md")),
                    "_children": {
                        "Что важно в покрытии": {"_text": load_content(content_path("insurance/medical/coverage.md")), "_children": {}},
                        "Амбулаторка vs стационар": {"_text": load_content(content_path("insurance/medical/opd_vs_ipd.md")), "_children": {}},
                        "Как пользоваться (cashless/не cashless)": {"_text": load_content(content_path("insurance/medical/how_to_use.md")), "_children": {}},
                        "Типовые отказы": {"_text": load_content(content_path("insurance/medical/denials.md")), "_children": {}},
                    },
                },
                "Путешествия": {
                    "_text": load_content(content_path("insurance/travel/intro.md")),
                    "_children": {
                        "Что должно быть в полисе": {"_text": load_content(content_path("insurance/travel/must_have.md")), "_children": {}},
                        "Спорт/байк/экстрим": {"_text": load_content(content_path("insurance/travel/sport_bike.md")), "_children": {}},
                        "Как оформить быстро": {"_text": load_content(content_path("insurance/travel/how_to_buy.md")), "_children": {}},
                    },
                },
                "Авто/байк": {
                    "_text": load_content(content_path("insurance/vehicle/intro.md")),
                    "_children": {
                        "Обязательная страховка": {"_text": load_content(content_path("insurance/vehicle/compulsory.md")), "_children": {}},
                        "Добровольная страховка": {"_text": load_content(content_path("insurance/vehicle/voluntary.md")), "_children": {}},
                        "ДТП: что делать": {"_text": load_content(content_path("insurance/vehicle/accident_steps.md")), "_children": {}},
                    },
                },
            },
        },

        # ==========================================================
        # ✅ 4) ⚠️ ПОВЕДЕНИЕ И КУЛЬТУРА
        # ==========================================================
        "⚠️ Поведение и культура": {
            "_text": "Поведение и культура — что важно знать в Таиланде.",
            "_children": {
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
            "_text": load_content(content_path("services/intro.md")),
            "_children": {
                "📱 Связь, SIM, интернет": {
                    "_text": load_content(content_path("services/sim_internet.md")),
                    "_children": {
                        "Как выбрать оператора": {"_text": load_content(content_path("services/sim/how_choose_operator.md")), "_children": {}},
                        "Где купить SIM": {"_text": load_content(content_path("services/sim/where_buy.md")), "_children": {}},
                        "Тарифы и пакеты": {"_text": load_content(content_path("services/sim/plans.md")), "_children": {}},
                        "Роуминг/раздача интернета": {"_text": load_content(content_path("services/sim/tethering_roaming.md")), "_children": {}},
                    },
                },
                "🚕 Такси и транспорт": {
                    "_text": load_content(content_path("services/taxi_transport.md")),
                    "_children": {
                        "Приложения такси": {"_text": load_content(content_path("services/transport/taxi_apps.md")), "_children": {}},
                        "Тук-туки/мототакси": {"_text": load_content(content_path("services/transport/tuktuk_moto.md")), "_children": {}},
                        "Аренда байка": {"_text": load_content(content_path("services/transport/bike_rent.md")), "_children": {}},
                        "Штрафы и документы": {"_text": load_content(content_path("services/transport/fines_docs.md")), "_children": {}},
                    },
                },
                "🍜 Доставка еды": {
                    "_text": load_content(content_path("services/food_delivery.md")),
                    "_children": {
                        "Какие приложения": {"_text": load_content(content_path("services/food/apps.md")), "_children": {}},
                        "Как заказывать (если не знаешь язык)": {"_text": load_content(content_path("services/food/how_order_no_language.md")), "_children": {}},
                        "Оплата и чаевые": {"_text": load_content(content_path("services/food/payment_tips.md")), "_children": {}},
                    },
                },
                "💳 Оплата, карты, кошельки": {
                    "_text": load_content(content_path("services/payments_cards_qr.md")),
                    "_children": {
                        "QR-оплата": {"_text": load_content(content_path("services/payments/qr.md")), "_children": {}},
                        "Наличные vs карта": {"_text": load_content(content_path("services/payments/cash_vs_card.md")), "_children": {}},
                        "Комиссии и конвертация": {"_text": load_content(content_path("services/payments/fees_fx.md")), "_children": {}},
                        "Блокировки и лимиты": {"_text": load_content(content_path("services/payments/blocks_limits.md")), "_children": {}},
                    },
                },
                "🛒 Магазины и закупки": {
                    "_text": load_content(content_path("services/shops_groceries.md")),
                    "_children": {
                        "Где покупать продукты": {"_text": load_content(content_path("services/shops/groceries_where.md")), "_children": {}},
                        "Бытовая химия/мелочи": {"_text": load_content(content_path("services/shops/household.md")), "_children": {}},
                        "Онлайн-заказы": {"_text": load_content(content_path("services/shops/online.md")), "_children": {}},
                    },
                },
                "🏠 Быт в квартире и доме": {
                    "_text": load_content(content_path("services/home_life.md")),
                    "_children": {
                        "Вода, питьё, фильтры": {"_text": load_content(content_path("services/home/water_filters.md")), "_children": {}},
                        "Электричество и техника": {"_text": load_content(content_path("services/home/electricity_appliances.md")), "_children": {}},
                        "Насекомые и профилактика": {"_text": load_content(content_path("services/home/insects.md")), "_children": {}},
                        "Стирка/прачечные": {"_text": load_content(content_path("services/home/laundry.md")), "_children": {}},
                    },
                },
                "📦 Доставки и посылки": {
                    "_text": load_content(content_path("services/delivery_packages.md")),
                    "_children": {
                        "Локальные доставки": {"_text": load_content(content_path("services/delivery/local.md")), "_children": {}},
                        "Международные посылки": {"_text": load_content(content_path("services/delivery/international.md")), "_children": {}},
                        "Что нельзя отправлять": {"_text": load_content(content_path("services/delivery/prohibited.md")), "_children": {}},
                    },
                },
                "🩺 Аптеки и базовая помощь": {
                    "_text": load_content(content_path("services/pharmacy_first_aid.md")),
                    "_children": {
                        "Как объяснить симптомы": {"_text": load_content(content_path("services/pharmacy/how_explain.md")), "_children": {}},
                        "Что иметь в аптечке": {"_text": load_content(content_path("services/pharmacy/first_aid_kit.md")), "_children": {}},
                        "Когда точно к врачу": {"_text": load_content(content_path("services/pharmacy/when_doctor.md")), "_children": {}},
                    },
                },
            },
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
