"""
Скрипт проверки целостности контента и меню FarangProBot.
Запуск: python3 validate_content.py
"""
import os
import sys
import hashlib
from typing import Dict, Any, List, Set, Tuple

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONTENT_DIR = os.path.join(BASE_DIR, "content")

_STUB_MARKERS = ("Этот раздел ещё заполняется", "Раздел находится в разработке")

errors: List[str] = []
warnings: List[str] = []


# ─── Импортируем MENU_TREE из main.py без запуска Telegram-бота ────────────
def load_menu_tree() -> Tuple[Dict, Dict, Dict]:
    import importlib.util, unittest.mock

    # Мокаем Telegram и sqlite3 чтобы не запускать реальные соединения
    telegram_mock = unittest.mock.MagicMock()
    sys.modules.setdefault("telegram", telegram_mock)
    sys.modules.setdefault("telegram.ext", telegram_mock)
    for sub in ["InlineKeyboardButton", "InlineKeyboardMarkup", "Update", "ReplyKeyboardRemove"]:
        sys.modules.setdefault(f"telegram.{sub}", telegram_mock)

    import sqlite3 as _sqlite3
    orig_connect = _sqlite3.connect
    _sqlite3.connect = unittest.mock.MagicMock(
        return_value=unittest.mock.MagicMock(
            cursor=unittest.mock.MagicMock(return_value=unittest.mock.MagicMock()),
            commit=unittest.mock.MagicMock(),
            close=unittest.mock.MagicMock(),
        )
    )

    spec = importlib.util.spec_from_file_location("main", os.path.join(BASE_DIR, "main.py"))
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception as e:
        errors.append(f"Не удалось загрузить main.py: {e}")
        return {}, {}, {}
    finally:
        _sqlite3.connect = orig_connect

    return mod.MENU_TREE, mod.ID_TO_PATH, mod.PATH_TO_ID


# ─── Утилиты ────────────────────────────────────────────────────────────────
def content_path(rel: str) -> str:
    return os.path.join(CONTENT_DIR, rel)


def is_stub(path: str) -> bool:
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
        return not text.strip() or any(m in text for m in _STUB_MARKERS)
    except FileNotFoundError:
        return False


def file_exists(rel: str) -> bool:
    return os.path.isfile(content_path(rel))


# ─── Обход дерева меню ──────────────────────────────────────────────────────
menu_files: Set[str] = set()        # _file пути, подключённые к меню
callback_data_set: Set[str] = set() # все callback_data для проверки дублей


def walk_tree(node: Dict[str, Any], path: List[str], depth: int = 0):
    if "_file" in node:
        rel = node["_file"]
        menu_files.add(rel)

        # 1. Файл существует?
        if not file_exists(rel):
            errors.append(f"MISSING FILE  | {rel}  (путь меню: {' > '.join(path) or 'root'})")

        # 2. Файл-заглушка?
        elif is_stub(content_path(rel)):
            warnings.append(f"STUB IN MENU  | {rel}  (покажет «Раздел готовится» — ОК)")

    # 3. Глубина не больше 3 уровней
    if depth > 3:
        warnings.append(f"DEEP MENU (depth={depth}) | {' > '.join(path)}")

    for name, child in node.get("_children", {}).items():
        # 4. Длина имени пункта (влияет на callback_data через MD5)
        if len(name) > 64:
            warnings.append(f"LONG BUTTON NAME ({len(name)} chars) | {name!r}")

        walk_tree(child, path + [name], depth + 1)


# ─── Callback_data дубли ────────────────────────────────────────────────────
def check_callback_duplicates(id_to_path: Dict):
    seen: Dict[str, str] = {}
    for node_id, pth in id_to_path.items():
        cb = f"nav:v5:{node_id}"
        if len(cb) > 64:
            errors.append(f"CALLBACK TOO LONG ({len(cb)}) | {cb}")
        if node_id in seen:
            errors.append(f"DUPLICATE NODE ID | {node_id}: {seen[node_id]} vs {pth}")
        seen[node_id] = str(pth)


# ─── Файлы контента без меню ────────────────────────────────────────────────
def check_orphaned_files():
    for root, _, files in os.walk(CONTENT_DIR):
        for fname in files:
            if not fname.endswith(".md"):
                continue
            abs_path = os.path.join(root, fname)
            rel = os.path.relpath(abs_path, CONTENT_DIR).replace("\\", "/")
            if rel not in menu_files:
                stub = is_stub(abs_path)
                tag = "STUB" if stub else "HAS_CONTENT"
                warnings.append(f"NOT IN MENU [{tag}] | content/{rel}")


# ─── Пустые файлы ────────────────────────────────────────────────────────────
def check_empty_files():
    for root, _, files in os.walk(CONTENT_DIR):
        for fname in files:
            if not fname.endswith(".md"):
                continue
            abs_path = os.path.join(root, fname)
            if os.path.getsize(abs_path) == 0:
                rel = os.path.relpath(abs_path, CONTENT_DIR).replace("\\", "/")
                errors.append(f"EMPTY FILE    | content/{rel}")


# ─── Кнопки Назад / Главное меню — проверяются в make_keyboard main.py ──────
# (Логика уже реализована в make_keyboard — кнопка «Назад» добавляется для
#  любого непустого пути, поэтому здесь только отмечаем это как ОК.)


# ─── Запуск ──────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("FarangProBot — проверка контента и меню")
    print("=" * 60)

    menu_tree, id_to_path, path_to_id = load_menu_tree()

    if not menu_tree:
        print("\n❌ Не удалось загрузить MENU_TREE. Проверь ошибки выше.")
        return

    print(f"\n✅ MENU_TREE загружен. Узлов: {len(id_to_path)}")

    walk_tree(menu_tree, [])
    check_callback_duplicates(id_to_path)
    check_orphaned_files()
    check_empty_files()

    print(f"\n📂 Файлов контента в меню: {len(menu_files)}")

    if errors:
        print(f"\n❌ ОШИБКИ ({len(errors)}):")
        for e in errors:
            print(f"  • {e}")
    else:
        print("\n✅ Ошибок не найдено.")

    if warnings:
        print(f"\n⚠️  ПРЕДУПРЕЖДЕНИЯ ({len(warnings)}):")
        for w in warnings:
            print(f"  • {w}")
    else:
        print("✅ Предупреждений нет.")

    print("\n" + "=" * 60)
    if errors:
        print(f"Итог: {len(errors)} ошибок, {len(warnings)} предупреждений.")
        sys.exit(1)
    else:
        print(f"Итог: всё в порядке. Предупреждений: {len(warnings)}.")


if __name__ == "__main__":
    main()
