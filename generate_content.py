import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONTENT_DIR = os.path.join(BASE_DIR, "content")

FILES = [
    # urgent
    ("urgent/intro.md", "🚨 Я только приехал / мне срочно"),
    ("urgent/thailand_not_paradise.md", "⚠️ Таиланд — не рай"),
    ("urgent/top5_mistakes.md", "❌ Топ-5 ошибок первых дней"),
    ("urgent/money_do_dont.md", "💱 Деньги: что можно / что нельзя"),
    ("urgent/visa_risks.md", "📄 Виза: где ты уже рискуешь"),
    ("urgent/rent_deposit.md", "🏠 Жильё: как не потерять депозит"),
    ("urgent/first_day_checklist.md", "🧰 Что сделать в первый день"),

    # visa
    ("visa/intro.md", "📄 Виза и легализация"),
    ("visa/which_visa.md", "❓ Какая виза мне подойдёт"),

    ("visa/ed/intro.md", "ED — учебная"),
    ("visa/ed/who_fits.md", "ED — кому подходит"),
    ("visa/ed/steps.md", "ED — пошагово"),
    ("visa/ed/risks.md", "ED — риски и ошибки"),

    ("visa/dtv/intro.md", "DTV — Digital Nomad"),
    ("visa/dtv/who_fits.md", "DTV — кому подходит"),
    ("visa/dtv/steps.md", "DTV — пошагово"),
    ("visa/dtv/risks.md", "DTV — риски и ошибки"),

    ("visa/family/intro.md", "Семейная виза"),
    ("visa/family/grounds.md", "Семейная — основания"),
    ("visa/family/steps.md", "Семейная — пошагово"),
    ("visa/family/risks.md", "Семейная — риски и ошибки"),

    ("visa/business/intro.md", "Бизнес-виза"),
    ("visa/business/who_fits.md", "Бизнес — кому подходит"),
    ("visa/business/steps.md", "Бизнес — пошагово"),
    ("visa/business/risks.md", "Бизнес — риски и ошибки"),

    ("visa/retirement/intro.md", "Пенсионная виза"),
    ("visa/retirement/requirements.md", "Пенсионная — требования"),
    ("visa/retirement/steps.md", "Пенсионная — пошагово"),
    ("visa/retirement/risks.md", "Пенсионная — риски"),

    ("visa/extensions/intro.md", "Продление штампов"),
    ("visa/extensions/where_how.md", "Продление — где и как"),
    ("visa/extensions/deadlines_fines.md", "Продление — сроки и штрафы"),
    ("visa/extensions/common_mistakes.md", "Продление — типовые ошибки"),

    # money_home
    ("money_home/intro.md", "💸 Деньги и жильё"),

    ("money_home/exchange/intro.md", "💱 Обмен и деньги"),
    ("money_home/exchange/where_best.md", "Где менять выгодно"),
    ("money_home/exchange/banks_vs_exchangers.md", "Банки vs обменники"),
    ("money_home/exchange/safety.md", "Безопасность при обмене"),

    ("money_home/rent/intro.md", "🏠 Аренда жилья"),
    ("money_home/rent/deposits_contracts.md", "Депозиты и контракты"),
    ("money_home/rent/agent_not_friend.md", "Агент ≠ твой друг"),
    ("money_home/rent/scams.md", "Типовые схемы развода"),

    ("money_home/payments/intro.md", "💳 Платежи и карты"),
    ("money_home/payments/cash_vs_cashless.md", "Нал vs безнал"),
    ("money_home/payments/cards_blocks.md", "Карты и блокировки"),
    ("money_home/payments/talk_to_bank.md", "Что говорить банку (честно и без мутных схем)"),

    # reality
    ("reality/intro.md", "⚠️ Реальность Таиланда"),

    ("reality/farang/intro.md", "🧠 Ты всегда фаранг"),
    ("reality/farang/what_it_means.md", "Что это значит"),
    ("reality/farang/smiles_not_friendship.md", "Улыбки ≠ дружба"),
    ("reality/farang/common_errors.md", "Где ошибаются чаще всего"),

    ("reality/helpers/intro.md", "🚩 Помогаторы"),
    ("reality/helpers/red_flags.md", "Красные флаги"),
    ("reality/helpers/schemes.md", "Типовые схемы"),
    ("reality/helpers/how_to_say_no.md", "Как отказывать"),

    ("reality/mistakes/intro.md", "😵 Типичные ошибки"),
    ("reality/mistakes/alcohol_aggression.md", "Алкоголь и агрессия"),
    ("reality/mistakes/bike_police.md", "Байк и полиция"),
    ("reality/mistakes/illegal_work.md", "Нелегальная работа"),

    ("reality/culture/intro.md", "🙏 Культура и поведение"),
    ("reality/culture/king_religion.md", "Король и религия"),
    ("reality/culture/temples_clothes.md", "Храмы и одежда"),
    ("reality/culture/lose_face.md", "Потеря лица"),

    # help
    ("help/intro.md", "🆘 Нужна помощь"),
    ("help/analyze_my_case.md", "🆘 Разобрать мою ситуацию"),
    ("help/ask_question.md", "💬 Задать вопрос"),
    ("help/checklists/intro.md", "📋 Чек-листы"),
    ("help/checklists/first_month.md", "Чек-лист: Первый месяц"),
    ("help/checklists/rent_no_losses.md", "Чек-лист: Аренда без потерь"),
    ("help/checklists/visa_no_extra.md", "Чек-лист: Виза без лишних расходов"),
    ("help/support_project.md", "☕ Поддержать проект"),
]

STUB_TEMPLATE = """# {title}

Этот раздел ещё заполняется.

**Что будет здесь:**
- кратко и по делу (без воды)
- пошаговые действия
- типовые ошибки и как их избежать

✅ Если хочешь — напиши, что именно ты хочешь видеть в этом пункте (2–3 тезиса).
"""

def ensure_file(rel_path: str, title: str):
    full_path = os.path.join(CONTENT_DIR, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    if not os.path.exists(full_path):
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(STUB_TEMPLATE.format(title=title))

def main():
    os.makedirs(CONTENT_DIR, exist_ok=True)
    for rel_path, title in FILES:
        ensure_file(rel_path, title)
    print(f"OK: создано/проверено файлов: {len(FILES)} в {CONTENT_DIR}")

if __name__ == "__main__":
    main()
