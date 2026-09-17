#!/usr/bin/env python3
import os
import re
import glob
import requests
from datetime import datetime

# --- ПУТИ К ФАЙЛАМ ---
VAULT_DIR = "/home/ravenchickd/obsidian_vault"
INBOX_DIR = os.path.join(VAULT_DIR, "00_Inbox")

inbox_matches = glob.glob(os.path.join(INBOX_DIR, "Дела на*.md"))
INBOX_FILE = inbox_matches[0] if inbox_matches else os.path.join(INBOX_DIR, "Дела на сегодня.md")

PROJECTS_DIR = os.path.join(VAULT_DIR, "10_Projects")
RESOURCES_DIR = os.path.join(VAULT_DIR, "20_Resources")
ARCHIVE_FILE = os.path.join(VAULT_DIR, "30_Archive/Completed_Log.md")
BACKLOG_FILE = os.path.join(PROJECTS_DIR, "Backlog.md")

# --- НАСТРОЙКИ HOME ASSISTANT ---
HA_BASE_URL = "http://127.0.0.1:8123/api"
HA_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIxZGU2MmQzYmJmMTA0ZTU2OWYxZmVhZmIyN2NlMmY3NiIsImlhdCI6MTc4MzU5NDc5MiwiZXhwIjoyMDk4OTU0NzkyfQ.4UpGlKlrsAb8s7KPnT1Lazv-Pvqd6ds0T-E-otkYS_I"
TODO_ENTITY_ID = "todo.tekushchie_dela_na_den"

HA_HEADERS = {
    "Authorization": f"Bearer {HA_TOKEN}",
    "Content-Type": "application/json",
}

# --- МАППИНГ ТЕГОВ ---
TAG_MAP = {
    # 10_Projects
    "волга": os.path.join(PROJECTS_DIR, "Волга/Волга.md"),
    "стройка": os.path.join(PROJECTS_DIR, "Стройка/Стройка.md"),
    "работа": os.path.join(PROJECTS_DIR, "Работа/Дела по работе.md"),
    "мордор": os.path.join(PROJECTS_DIR, "План Мордор/План Мордор.md"),
    "мастит": os.path.join(PROJECTS_DIR, "Mastitis/Mastitis.md"),
    "mastitis": os.path.join(PROJECTS_DIR, "Mastitis/Mastitis.md"),
    "сад": os.path.join(PROJECTS_DIR, "Home_Garden/По саду.md"),
    "дом": os.path.join(PROJECTS_DIR, "Home_Garden/По квартире.md"),

    # 02_Learning
    "docker": os.path.join(VAULT_DIR, "02_Learning/Docker/2026-09-02-Docker-Log.md"),
    "докер": os.path.join(VAULT_DIR, "02_Learning/Docker/2026-09-02-Docker-Log.md"),
    "study": os.path.join(VAULT_DIR, "02_Learning/Science_Research/Научные заметки_0046.md"),
    "наука": os.path.join(VAULT_DIR, "02_Learning/Science_Research/Научные заметки_0046.md"),
    "bio": os.path.join(VAULT_DIR, "02_Learning/Science_Research/Научные заметки_0046.md"),

    # 20_Resources
    "деньги": os.path.join(RESOURCES_DIR, "Finance/Учёт расходов_0013.md"),
    "финансы": os.path.join(RESOURCES_DIR, "Finance/Учёт расходов_0013.md"),
    "зубы": os.path.join(RESOURCES_DIR, "Health/ЗУБЫ_0030.md"),
    "здоровье": os.path.join(RESOURCES_DIR, "Health/ЗУБЫ_0030.md"),
    "соседи": os.path.join(RESOURCES_DIR, "Home_Garden/Соседи.md"),
    "любимая": os.path.join(RESOURCES_DIR, "Personal/Любимая/Подарки Саше.md"),
    "кудасходить": os.path.join(RESOURCES_DIR, "Personal/Куда сходить/Места.md"),
    "досуг": os.path.join(RESOURCES_DIR, "Personal/Куда сходить/Места.md"),
    "др": os.path.join(RESOURCES_DIR, "Personal/Дни рождения_0036.md"),
    "железо": os.path.join(RESOURCES_DIR, "Tech_Hardware/Компы_0021.md"),
    "пк": os.path.join(RESOURCES_DIR, "Tech_Hardware/Компы_0021.md"),
    "steam": os.path.join(RESOURCES_DIR, "Media_Hobbies/Для steam_0015.md"),
}

def append_to_file(file_path, text):
    """Дописывает строку в файл."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(text + "\n")

def clear_ha_todo_list():
    """Очищает дашборд Home Assistant."""
    url_get = f"{HA_BASE_URL}/services/todo/get_items"
    payload = {"entity_id": TODO_ENTITY_ID, "status": ["needs_action", "completed"]}
    
    try:
        res_get = requests.post(url_get, json=payload, headers=HA_HEADERS, timeout=5)
        items_to_remove = []
        if res_get.status_code == 200:
            res_data = res_get.json()
            for res in res_data:
                for item in res.get("response", {}).get(TODO_ENTITY_ID, {}).get("items", []):
                    items_to_remove.append(item.get("summary"))

        if not items_to_remove:
            return

        url_remove = f"{HA_BASE_URL}/services/todo/remove_item"
        for item_summary in set(items_to_remove):
            if not item_summary:
                continue
            rem_payload = {"entity_id": TODO_ENTITY_ID, "item": item_summary}
            requests.post(url_remove, json=rem_payload, headers=HA_HEADERS, timeout=5)

    except Exception as e:
        print(f"[HA] Ошибка очистки Home Assistant: {e}")

def get_target_file(raw_line):
    tags = re.findall(r"#([\w/А-Яа-яЁё]+)", raw_line)
    for tag in tags:
        tag_lower = tag.lower()
        if tag_lower in TAG_MAP:
            return TAG_MAP[tag_lower]
    return BACKLOG_FILE

def clean_completed_from_file(file_path):
    """Удаляет выполненные задачи [- [x]] из файла и отправляет их в Архив."""
    if not os.path.exists(file_path):
        return 0

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    archived_count = 0
    today_str = datetime.now().strftime("%Y-%m-%d")

    for line in lines:
        raw_line = line.strip()
        # Если это закрытая задача -> переносим в Архив
        if re.match(r"^\s*-\s*\[[xX]\]", raw_line):
            append_to_file(ARCHIVE_FILE, f"- [{today_str}] {raw_line}")
            archived_count += 1
        else:
            new_lines.append(line)

    if archived_count > 0:
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

    return archived_count

def process_nightly_inbox():
    if not os.path.exists(INBOX_FILE):
        print(f"Файл {INBOX_FILE} не найден.")
        return

    with open(INBOX_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    remaining_lines = []
    moved_active = 0
    deleted_completed = 0

    for line in lines:
        raw_line = line.strip()

        # 1. Завершенные задачи [- [x]] -> стираем навсегда (не сохраняем)
        if re.match(r"^\s*-\s*\[[xX]\]", raw_line):
            deleted_completed += 1
            continue

        # 2. Незавершенные задачи [- [ ]] -> переносим в Backlog/Проект
        if re.match(r"^\s*-\s*\[\s*\]", raw_line):
            target_path = get_target_file(raw_line)
            append_to_file(target_path, raw_line)
            moved_active += 1
            continue

        # 3. Все остальное (мысли, заметки, wiki-ссылки [[...]]) -> оставляем в файле
        remaining_lines.append(line)

    # Перезаписываем Инбокс: сохраняем заголовок и мысли/заметки
    with open(INBOX_FILE, "w", encoding="utf-8") as f:
        if not remaining_lines or not remaining_lines[0].startswith("# "):
            f.write("# Дела на сегодня\n\n")
        f.writelines(remaining_lines)

    # --- ОЧИСТКА БЭКЛОГА И ПРОЕКТОВ ОТ ВЫПОЛНЕННЫХ ЗАДАЧ ---
    total_archived = clean_completed_from_file(BACKLOG_FILE)
    for target_file in set(TAG_MAP.values()):
        total_archived += clean_completed_from_file(target_file)

    print(f"[{datetime.now()}] Разбор завершен.")
    print(f"- Удалено закрытых из Инбокса: {deleted_completed}")
    print(f"- Перенесено активных в Бэклог/Проекты: {moved_active}")
    print(f"- Отправлено в Архив из Бэклога/Проектов: {total_archived}")

    clear_ha_todo_list()

if __name__ == "__main__":
    process_nightly_inbox()
