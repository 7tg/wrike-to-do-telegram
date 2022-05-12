import requests
import datetime
import argparse

URL = "https://www.wrike.com/api/v4/tasks"

DAY_NAME = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']


def get_tasks(account_id: str, wrike_token: str) -> list[dict]:
    query = {
        "responsibles": f'["{account_id}"]',
        "status": "Active",
        "fields": '["subTaskIds"]',
    }

    headers = {
        'Authorization': f'bearer {wrike_token}'
    }
    response = requests.get(URL, params=query, headers=headers)
    response.raise_for_status()
    return response.json()["data"]


def build_daily_string(tasks: list[dict]) -> str:
    today = datetime.datetime.now()
    daily_str = f"{DAY_NAME[today.weekday()]}:\n"
    daily_str += "\n".join([f"- {task['title']}" for task in reversed(tasks) if not task["subTaskIds"]])

    return daily_str


def send_telegram_message(
    body,
    chats,
    telegram_token
):
    for chat in chats:
        params = {
            'chat_id': chat,
            'text': body,
        }
        res = requests.post(
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
    tasks = get_tasks(args.accountId, args.wrikeToken)
    daily_str = build_daily_string(tasks)
    send_telegram_message(
        daily_str,
        [args.telegramChat, ],
        args.telegramToken
    )


if __name__ == '__main__':
    main()
