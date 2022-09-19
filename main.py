import argparse
import datetime
from typing import List, Tuple

import requests
from requests import Response

URL = "https://www.wrike.com/api/v4/tasks"

DAY_NAME = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']


def get_tasks(account_id: str, wrike_token: str) -> Tuple[List[dict], List[dict]]:
    query = {
        "responsibles": f'["{account_id}"]',
        "status": "Active",
        "fields": '["subTaskIds", "description", "parentIds"]',
    }

    headers = {
        'Authorization': f'bearer {wrike_token}'
    }
    response = requests.get(URL, params=query, headers=headers)
    response.raise_for_status()

    folders_res = requests.get("https://www.wrike.com/api/v4/folders", headers=headers)
    folders_res.raise_for_status()

    return response.json()["data"], folders_res.json()["data"]


def build_daily_string(tasks: List[dict], folders: List[dict]) -> str:
    today = datetime.datetime.now()
    daily_str = f"{DAY_NAME[today.weekday()]}:\n"

    filtered_tasks = [
            task
            for task in reversed(tasks)
            if not task["subTaskIds"]
               and "https://gitlab.com" not in task["description"]
        ]
    for task in filtered_tasks:
        task_folders = list(filter(lambda folder: folder["id"] in task["parentIds"], folders))
        folder_name = ",".join([folder["title"] for folder in task_folders]) if task_folders else None

        task_str = f"- [Link]({task['permalink']}) / {task['title']}"
        task_str += f" ({folder_name})\n" if folder_name else "\n"
        daily_str += task_str

    return daily_str


def send_telegram_message(
    body: str,
    chat: str,
    telegram_token: str
) -> Response:
    params = {
        'chat_id': chat,
        'text': body,
    }
    return requests.post(
        f'https://api.telegram.org/bot{telegram_token}/sendMessage',
        params=params
    )


def main():
    parser = argparse.ArgumentParser(description='Script that fetches your to-do tasks and prints daily message '
                                                 'according to info')
    parser.add_argument(
        '--accountId', '-ai',
        required=True,
        help='Account Id'
    )
    parser.add_argument(
        '--wrikeToken', '-wt',
        required=True,
        help='Wrike Token'
    )
    parser.add_argument(
        '--telegramToken', '-tt',
        required=True,
        help='Telegram Token'
    )
    parser.add_argument(
        '--telegramChat', '-tc',
        required=True,
        help='Telegram Chat'
    )
    args = parser.parse_args()
    today = datetime.datetime.now()
    if today.weekday() > 4:
        return
    tasks, folders = get_tasks(args.accountId, args.wrikeToken)
    daily_str = build_daily_string(tasks, folders)
    send_telegram_message(
        daily_str,
        args.telegramChat,
        args.telegramToken
    )


if __name__ == '__main__':
    main()
