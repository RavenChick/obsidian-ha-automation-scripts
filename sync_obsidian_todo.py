import os
import re
import requests

# --- НАСТРОЙКИ ---
VAULT_PATH = os.getenv("OBSIDIAN_INBOX_FILE", "/home/user/obsidian_vault/00_Inbox/Today.md")
HA_BASE_URL = os.getenv("HA_BASE_URL", "http://127.0.0.1:8123/api")
HA_TOKEN = os.getenv("HA_TOKEN", "YOUR_HOME_ASSISTANT_LONG_LIVED_TOKEN")
TODO_ENTITY_ID = "todo.tekushchie_dela_na_den"

HEADERS = {
    "Authorization": f"Bearer {HA_TOKEN}",
    "Content-Type": "application/json",
}

def get_active_tasks_from_obsidian(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return []
    
    tasks = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            match = re.match(r"^\s*-\s*\[\s*\]\s+(.+)$", line)
            if match:
                task_text = match.group(1).strip()
                if task_text:
                    tasks.append(task_text)
    return tasks

def parse_ha_items_via_service():
    url = f"{HA_BASE_URL}/services/todo/get_items"
    payload = {"entity_id": TODO_ENTITY_ID}
    try:
        response = requests.post(url, json=payload, headers=HEADERS, timeout=5)
        if response.status_code == 200:
            results = response.json()
            items = []
            for res in results:
                for item in res.get("response", {}).get(TODO_ENTITY_ID, {}).get("items", []):
                    if item.get("status") == "needs_action":
                        items.append(item.get("summary", "").strip())
            return items
    except Exception as e:
        print(f"Failed to fetch tasks via service: {e}")
    return []

def get_existing_tasks_from_ha():
    url = f"{HA_BASE_URL}/states/{TODO_ENTITY_ID}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=5)
        if response.status_code == 200:
            return parse_ha_items_via_service()
        else:
            print(f"Error getting HA status ({response.status_code})")
            return []
    except Exception as e:
        print(f"Network error: {e}")
        return []

def add_task_to_ha(task_text):
    url = f"{HA_BASE_URL}/services/todo/add_item"
    payload = {
        "entity_id": TODO_ENTITY_ID,
        "item": task_text
    }
    try:
        response = requests.post(url, json=payload, headers=HEADERS, timeout=5)
        if response.status_code == 200:
            print(f"Added task: {task_text}")
        else:
            print(f"Error adding task ({response.status_code}): {response.text}")
    except Exception as e:
        print(f"Network error during add: {e}")

if __name__ == "__main__":
    print("Checking lists...")
    obsidian_tasks = get_active_tasks_from_obsidian(VAULT_PATH)
    
    if not obsidian_tasks:
        print("No active tasks in Obsidian.")
        exit()
        
    ha_tasks = get_existing_tasks_from_ha()
    print(f"Found tasks in HA: {len(ha_tasks)}")
    
    added_count = 0
    for task in obsidian_tasks:
        if task in ha_tasks:
            continue
        
        add_task_to_ha(task)
        added_count += 1
        
    if added_count == 0:
        print("All tasks are in sync. No duplicates.")
