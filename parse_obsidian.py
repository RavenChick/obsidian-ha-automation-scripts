#!/usr/bin/env python3
import os
import re
import glob
import requests
from datetime import datetime

# --- ПУТИ К ФАЙЛАМ ---
VAULT_DIR = os.getenv("OBSIDIAN_VAULT_PATH", "/home/user/obsidian_vault")
INBOX_DIR = os.path.join(VAULT_DIR, "00_Inbox")

inbox_matches = glob.glob(os.path.join(INBOX_DIR, "Дела на*.md"))
INBOX_FILE = inbox_matches[0] if inbox_matches else os.path.join(INBOX_DIR, "Дела на сегодня.md")

PROJECTS_DIR = os.path.join(VAULT_DIR, "10_Projects")
RESOURCES_DIR = os.path.join(VAULT_DIR, "20_Resources")
ARCHIVE_FILE = os.path.join(VAULT_DIR, "30_Archive/Completed_Log.md")
BACKLOG_FILE = os.path.join(PROJECTS_DIR, "Backlog.md")

# --- НАСТРОЙКИ HOME ASSISTANT ---
HA_BASE_URL = os.getenv("HA_BASE_URL", "http://127.0.0.1:8123/api")
HA_TOKEN = os.getenv("HA_TOKEN", "YOUR_HOME_ASSISTANT_LONG_LIVED_TOKEN")
TODO_ENTITY_ID = "todo.tekushchie_dela_na_den"

HA_HEADERS = {
    "Authorization": f"Bearer {HA_TOKEN}",
    "Content-Type": "application/json",
}

# --- МАППИНГ ТЕГОВ ---
TAG_MAP = {
    "projects": os.path.join(PROJECTS_DIR, "Projects.md"),
    "work": os.path.join(PROJECTS_DIR, "Work.md"),
    "docker": os.path.join(VAULT_DIR, "02_Learning/Docker/Docker-Log.md"),
    "study": os.path.join(VAULT_DIR, "02_Learning/Science/Research.md"),
    "finance": os.path.join(RESOURCES_DIR, "Finance/Expenses.md"),
    "tech": os.path.join(RESOURCES_DIR, "Tech_Hardware/PC.md"),
}

def append_to_file(file_path, text):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(text + "\n")

def clear_ha_todo_list():
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
        print(f"[HA] Error clearing Home Assistant todo items: {e}")

def get_target_file(raw_line):
    tags = re.findall(r"#([\w/А-Яа-яЁё]+)", raw_line)
    for tag in tags:
        tag_lower = tag.lower()
        if tag_lower in TAG_MAP:
            return TAG_MAP[tag_lower]
    return BACKLOG_FILE

def clean_completed_from_file(file_path):
    if not os.path.exists(file_path):
        return 0

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    archived_count = 0
    today_str = datetime.now().strftime("%Y-%m-%d")

    for line in lines:
        raw_line = line.strip()
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
        print(f"File {INBOX_FILE} not found.")
        return

    with open(INBOX_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    remaining_lines = []
    moved_active = 0
    deleted_completed = 0

    for line in lines:
        raw_line = line.strip()

        if re.match(r"^\s*-\s*\[[xX]\]", raw_line):
            deleted_completed += 1
            continue

        if re.match(r"^\s*-\s*\[\s*\]", raw_line):
            target_path = get_target_file(raw_line)
            append_to_file(target_path, raw_line)
            moved_active += 1
            continue

        remaining_lines.append(line)

    with open(INBOX_FILE, "w", encoding="utf-8") as f:
        if not remaining_lines or not remaining_lines[0].startswith("# "):
            f.write("# Tasks for today\n\n")
        f.writelines(remaining_lines)

    total_archived = clean_completed_from_file(BACKLOG_FILE)
    for target_file in set(TAG_MAP.values()):
        total_archived += clean_completed_from_file(target_file)

    print(f"[{datetime.now()}] Inbox parse completed.")
    print(f"- Deleted finished from inbox: {deleted_completed}")
    print(f"- Moved active to backlog: {moved_active}")
    print(f"- Sent to archive: {total_archived}")

    clear_ha_todo_list()

if __name__ == "__main__":
    process_nightly_inbox()
