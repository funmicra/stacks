#!/usr/bin/env python3
import os
import requests
import subprocess
from pathlib import Path
from dotenv import load_dotenv
from itertools import zip_longest
from prettytable import PrettyTable
from datetime import datetime
from pathlib import Path

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()

ENABLE_TELEGRAM = os.getenv("ENABLE_TELEGRAM", "False").lower() in ("1", "true", "yes")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
WORK_DIR = os.getenv("WORK_DIR", str(Path.cwd()))  # default to current directory
parent_path = Path(WORK_DIR)

if not parent_path.exists():
    raise FileNotFoundError(f"{WORK_DIR} does not exist")

WORK_DIR_PATH = Path(WORK_DIR)
WORK_DIR_PATH.mkdir(parents=True, exist_ok=True)
LOG_FILE = WORK_DIR_PATH / "deployments.log"

def log_deployment(folder_name, action, status):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Open in append mode, creates file if it doesn't exist
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(f"{timestamp} | {folder_name} | {action} | {status}\n")

def send_telegram_message(message: str):
    if not ENABLE_TELEGRAM:
        return  # Telegram is disabled

    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram not configured. Skipping message.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        r = requests.post(url, data=payload, timeout=5)
        if not r.ok:
            print(f"⚠️ Failed to send Telegram message: {r.text}")
    except Exception as e:
        print(f"⚠️ Telegram error: {e}")

# -----------------------------
# List subfolders
# -----------------------------
subfolders = [f for f in parent_path.iterdir() if f.is_dir()]
if not subfolders:
    print("🐳 No Apps found.")
    exit()

# Display in two columns with numbers
half = (len(subfolders) + 1) // 2
col1 = subfolders[:half]
col2 = subfolders[half:]

print("🐳 Apps found:")
for i, (f1, f2) in enumerate(zip_longest(col1, col2, fillvalue=None), start=1):
    num1 = i
    num2 = i + half if f2 else ""
    line = f"{num1}. {f1.name:25}"  # left column
    if f2:
        line += f"{num2}. {f2.name}"  # right column
    print(line)

# -----------------------------
# Select folders
# -----------------------------
selected_input = input(
    "\nEnter the numbers of the subfolders you want to deploy (comma-separated, e.g., 1,3,5): "
)
try:
    selected_indices = [int(i.strip()) - 1 for i in selected_input.split(",") if i.strip()]
except ValueError:
    print("Invalid input. Please enter numbers separated by commas.")
    exit()

if not selected_indices:
    print("No folders selected. Exiting.")
    exit()

# -----------------------------
# Select action with custom validation
# -----------------------------
while True:
    action_input = input(
        "Do you want to 'up' or 'down' the docker-compose? "
        "[Up/Down]:"
    ).strip()

    if action_input in ("up", "Y", "y", "U", "u", "1"):
        action = "up"
        break
    elif action_input in ("down", "D", "d", "0"):
        action = "down"
        break
    else:
        print("Invalid input. Please enter a valid choice for 'up' or 'down'.")


# -----------------------------
# Confirm action with input validation
# -----------------------------
while True:
    confirm = input(f"Are you sure for '{action}' the selected containers? [y/N]: ").strip().lower()
    if confirm == 'y':
        break  # proceed
    elif confirm == 'n' or confirm == '':
        print("Aborted.")
        exit()
    else:
        print("Invalid input. Please enter 'y' or 'N'.")

results = []

# -----------------------------
# Perform docker compose
# -----------------------------
for idx in selected_indices:
    if idx < 0 or idx >= len(subfolders):
        continue

    folder = subfolders[idx]
    compose_file = folder / "docker-compose.yaml"
    if compose_file.exists():
        cmd = ["docker", "compose", "-f", str(compose_file), action]
        if action == "up":
            cmd.extend(["-d", "--build"])

        result = subprocess.run(cmd, cwd=folder)
        status = "Success ✅" if result.returncode == 0 else "Failed ❌"
        log_deployment(folder.name, action, status)
        send_telegram_message(f"{folder.name} {status} {action.upper()}")
        results.append((folder.name, action, status))
    else:
        results.append((folder.name, "No docker-compose.yaml"))

# -----------------------------
# Print summary table
# -----------------------------
table = PrettyTable()
table.field_names = ["App", "Action", "Status"]
for app, action, status in results:
    table.add_row([app, action, status])

print("\nDeployment Summary:")
print(table)