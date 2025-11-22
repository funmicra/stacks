## Multi-Compose Deployment Orchestrator

This project provides an interactive command-line utility designed to streamline operational workflows across multiple Docker Compose stacks. By centralizing the discovery, selection, and execution logic, the tool eliminates repetitive manual effort and enables consistent, audit-ready deployments at scale.


## Overview

The orchestrator automatically scans a defined parent directory, indexes all subfolders that contain Docker Compose workloads, and presents them in an interactive, two-column selection interface. Users can deploy or undeploy multiple stacks in a single execution.

The solution is optimized for environments with many composed micro-services, labs, and multi-stack environments where fast iteration and consistent lifecycle management are required.



## Key Capabilities

- Auto-discovers subfolders containing docker-compose.yaml
- Presents items in an indexed two-column interactive selector
- Supports multi-selection deployments and teardowns
- Executes docker **compose up -d** or **docker compose down**
- Contains .env.example for rapid deloyment (In some apps is missing, i will add it soon)
- Generates a deployment summary table after execution
- Writes persistent deployment logs (deployments.log)
- Optional Telegram notifications via .env toggle
- Fully environment-driven configuration



## Requirements

- Python 3.9+
- Docker & Docker Compose plugin
- python-dotenv
- prettytable
- requests (only if Telegram notifications are enabled)

Install Python dependencies:
```bash
pip install -r requirements.txt
```



## Configuration

All configuration is controlled via .env:

```ini
# Base directory for stack discovery
WORK_DIR=/path/to/your/stacks

# Telegram notifications (optional)
ENABLE_TELEGRAM=True (If empty, by default is false)
TELEGRAM_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```
Subfolders can each contain their own .env files; Mine remain ignored via .gitignore.



## Usage

1. Create a docker network:
```bash
docker network create Apps-Network
```

2. Run the orchestrator:
```bash
python3 multi-compose.py
```

The tool will:
1. Scan WORK_DIR
2. Display all subfolders in structured columns as App Name
3. Prompt for folder selection (multi-select supported)
4. Prompt for desired action (up or down)
5. Request confirmation via validated prompts
6. Execute Compose actions in the selected directories
7. Generate a deployment summary table
8. Persist results to deployments.log
9. Optionally push alerts to Telegram
