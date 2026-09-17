# Obsidian Vault & Server Automation Suite

A collection of Python and Bash automation utilities deployed on a home server for managing Obsidian markdown structures, task tracking with Home Assistant, and gateway routing.

## Overview & Included Scripts

### 1. `parse_obsidian.py`
Automated parser for Obsidian vault notes. Reads markdown tasks, organizes active items into project/backlog structures, archives completed tasks, and clears daily tracking lists via Home Assistant REST API.

### 2. `sync_obsidian_todo.py`
Task synchronization script. Parses pending checklist items (`- [ ]`) from daily Obsidian notes and syncs them directly into Home Assistant To-Do entities without producing duplicates.

### 3. `start-gateway.sh`
System bootstrap and network gateway configuration shell script. Handles routing initialization (Xray TProxy) and Wi-Fi Access Point creation via `lnxrouter`.

## Setup & Configuration

### Environment Variables
For security, pass credentials via system environment variables instead of hardcoding:

```bash
export HA_BASE_URL="[http://127.0.0.1:8123/api](http://127.0.0.1:8123/api)"
export HA_TOKEN="your_long_lived_access_token"
export OBSIDIAN_VAULT_PATH="/path/to/your/obsidian_vault"

ch Stack
Languages: Python 3, Bash (Shell)

Integrations: Home Assistant REST API, Obsidian Markdown Architecture

Environment: Debian Linux, Systemd Services
