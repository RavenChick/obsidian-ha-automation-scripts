import os
import re
import requests

# --- НАСТРОЙКИ ---
VAULT_PATH = "/home/ravenchickd/obsidian_vault/00_Inbox/Дела на  сегодня.md"
HA_BASE_URL = "http://127.0.0.1:8123/api"
HA_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIxZGU2MmQzYmJmMTA0ZTU2OWYxZmVhZmIyN2NlMmY3NiIsImlhdCI6MTc4MzU5NDc5MiwiZXhwIjoyMDk4OTU0NzkyfQ.4UpGlKlrsAb8s7KPnT1Lazv-Pvqd6ds0T-E-otkYS_I"
TODO_ENTITY_ID = "todo.tekushchie_dela_na_den"
# ------------------

HEADERS = {
    "Authorization": f"Bearer {HA_TOKEN}",
    "Content-Type": "application/json",
}

def get_active_tasks_from_obsidian(file_path):
    if not os.path.exists(file_path):
        print(f"Ошибка: Файл {file_path} не найден.")
        return []
    
    tasks = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            # Ищем невыполненные чекбоксы: - [ ] Текст задачи
            match = re.match(r"^\s*-\s*\[\s*\]\s+(.+)$", line)
            if match:
                task_text = match.group(1).strip()
                if task_text:
                    tasks.append(task_text)
    return tasks

def get_existing_tasks_from_ha():
    url = f"{HA_BASE_URL}/states/{TODO_ENTITY_ID}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=5)
        if response.status_code == 200:
            data = response.json()
            # Достаем список активных задач из атрибутов сущности todo
            # В зависимости от версии HA они лежат в разных полях, проверим стандартные варианты
            todo_list = data.get("attributes", {}).get("todo_items", [])
            
            # Если это современный local_todo, список может быть пуст в стейте, 
            # тогда мы запрашиваем его через сервис (надежный вариант)
            return parse_ha_items_via_service()
        else:
            print(f"Ошибка получения статуса HA ({response.status_code})")
            return []
    except Exception as e:
        print(f"Ошибка сети при запросе списка: {e}")
        return []

def parse_ha_items_via_service():
    # Запрашиваем актуальный список задач через вызов сервиса todo.get_items
    url = f"{HA_BASE_URL}/services/todo/get_items"
    payload = {"entity_id": TODO_ENTITY_ID}
    try:
        response = requests.post(url, json=payload, headers=HEADERS, timeout=5)
        if response.status_code == 200:
            results = response.json()
            # Парсим ответ структуры сервиса
            items = []
            for res in results:
                for item in res.get("response", {}).get(TODO_ENTITY_ID, {}).get("items", []):
                    # Нас интересуют только незавершенные задачи (status == "needs_action")
                    if item.get("status") == "needs_action":
                        items.append(item.get("summary", "").strip())
            return items
    except Exception as e:
        print(f"Не удалось получить задачи через сервис: {e}")
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
            print(f"Добавлено: {task_text}")
        else:
            print(f"Ошибка добавления ({response.status_code}): {response.text}")
    except Exception as e:
        print(f"Ошибка сети при добавлении: {e}")

if __name__ == "__main__":
    print("Проверка списков...")
    obsidian_tasks = get_active_tasks_from_obsidian(VAULT_PATH)
    
    if not obsidian_tasks:
        print("В Obsidian нет активных задач.")
        exit()
        
    ha_tasks = get_existing_tasks_from_ha()
    print(f"Найдено задач в HA: {len(ha_tasks)}")
    
    added_count = 0
    for task in obsidian_tasks:
        # Сравниваем текст (без учета лишних пробелов на всякий случай)
        if task in ha_tasks:
            # Задача уже есть в Home Assistant, пропускаем
            continue
        
        add_task_to_ha(task)
        added_count += 1
        
    if added_count == 0:
        print("Все задачи уже синхронизированы. Дубликатов нет.")import os
import re
import requests

# --- НАСТРОЙКИ ---
VAULT_PATH = "/home/ravenchickd/Markdowns/00_Inbox/Дела на  сегодня.md"
HA_BASE_URL = "http://127.0.0.1:8123/api"
HA_TOKEN = "ВСТАВЬ_СЮДА_СВОЙ_ТОКЕН"
TODO_ENTITY_ID = "todo.tekushchie_dela_na_den"
# ------------------

HEADERS = {
    "Authorization": f"Bearer {HA_TOKEN}",
    "Content-Type": "application/json",
}

def get_active_tasks_from_obsidian(file_path):
    if not os.path.exists(file_path):
        print(f"Ошибка: Файл {file_path} не найден.")
        return []
    
    tasks = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            # Ищем невыполненные чекбоксы: - [ ] Текст задачи
            match = re.match(r"^\s*-\s*\[\s*\]\s+(.+)$", line)
            if match:
                task_text = match.group(1).strip()
                if task_text:
                    tasks.append(task_text)
    return tasks

def get_existing_tasks_from_ha():
    url = f"{HA_BASE_URL}/states/{TODO_ENTITY_ID}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=5)
        if response.status_code == 200:
            data = response.json()
            # Достаем список активных задач из атрибутов сущности todo
            # В зависимости от версии HA они лежат в разных полях, проверим стандартные варианты
            todo_list = data.get("attributes", {}).get("todo_items", [])
            
            # Если это современный local_todo, список может быть пуст в стейте, 
            # тогда мы запрашиваем его через сервис (надежный вариант)
            return parse_ha_items_via_service()
        else:
            print(f"Ошибка получения статуса HA ({response.status_code})")
            return []
    except Exception as e:
        print(f"Ошибка сети при запросе списка: {e}")
        return []

def parse_ha_items_via_service():
    # Запрашиваем актуальный список задач через вызов сервиса todo.get_items
    url = f"{HA_BASE_URL}/services/todo/get_items"
    payload = {"entity_id": TODO_ENTITY_ID}
    try:
        response = requests.post(url, json=payload, headers=HEADERS, timeout=5)
        if response.status_code == 200:
            results = response.json()
            # Парсим ответ структуры сервиса
            items = []
            for res in results:
                for item in res.get("response", {}).get(TODO_ENTITY_ID, {}).get("items", []):
                    # Нас интересуют только незавершенные задачи (status == "needs_action")
                    if item.get("status") == "needs_action":
                        items.append(item.get("summary", "").strip())
            return items
    except Exception as e:
        print(f"Не удалось получить задачи через сервис: {e}")
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
            print(f"Добавлено: {task_text}")
        else:
            print(f"Ошибка добавления ({response.status_code}): {response.text}")
    except Exception as e:
        print(f"Ошибка сети при добавлении: {e}")

if __name__ == "__main__":
    print("Проверка списков...")
    obsidian_tasks = get_active_tasks_from_obsidian(VAULT_PATH)
    
    if not obsidian_tasks:
        print("В Obsidian нет активных задач.")
        exit()
        
    ha_tasks = get_existing_tasks_from_ha()
    print(f"Найдено задач в HA: {len(ha_tasks)}")
    
    added_count = 0
    for task in obsidian_tasks:
        # Сравниваем текст (без учета лишних пробелов на всякий случай)
        if task in ha_tasks:
            # Задача уже есть в Home Assistant, пропускаем
            continue
        
        add_task_to_ha(task)
        added_count += 1
        
    if added_count == 0:
        print("Все задачи уже синхронизированы. Дубликатов нет.")
