# Obsidian Vault & Server Automation Suite

A collection of Python and Bash automation utilities deployed on a Debian home server for managing Obsidian markdown structures, task tracking, and gateway routing.

## Overview & Included Scripts

### 1. `parse_obsidian.py`
Automated parser for Obsidian vault notes. Reads markdown AST/metadata, cleans up frontmatter formatting, and generates structured index files or daily status summaries.

### 2. `sync_obsidian_todo.py`
Task management and synchronization script. Parses todo lists (`- [ ]` / `- [x]`) across daily notes, archives completed tasks, and pushes updates via local APIs.

### 3. `start-gateway.sh`
System bootstrap and network gateway configuration shell script. Handles routing initialization, service dependency checks, and environment setup on startup.

## Deployment & Usage

### Prerequisites
- Python 3.10+
- Linux (Debian/Ubuntu) server environment

### Execution Examples
```bash
# Parse Obsidian vault metadata
python3 parse_obsidian.py

# Sync and archive Obsidian todo tasks
python3 sync_obsidian_todo.py

# Execute gateway service runner
bash start-gateway.sh

Tech Stack
Languages: Python 3, Bash (Shell)

Environment: Debian Linux, systemd cron/timers

Data Formats: Markdown, JSON, YAML
