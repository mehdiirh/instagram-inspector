[![Black](https://github.com/mehdiirh/instagram-inspector/actions/workflows/black.yml/badge.svg)](https://github.com/mehdiirh/instagram-inspector/actions/workflows/black.yml)

# 🤖 Instagram Inspector
### Inspect users on Instagram. Get notifications on Telegram when they follow/unfollow someone.

## 📍 Features
<li>Inspect followers changes</li>
<li>Inspect followings changes</li>
<li>Setting proxy</li>
<li>Get notifications in a Telegram channel</li>

## ⚙️ Initialization
1 - Make a copy of sample.env and name it `.env`:
```bash
cp sample.env .env
```

2 - Make a copy of database and name it `database.sqlite3`:
```bash
cp database-sample.sqlite3 database.sqlite3
```
3 - Get an API_ID and API_HASH from telegram [using this link](https://core.telegram.org/api/obtaining_api_id).

4 - Create a Telegram bot using [t.me/BotFather](https://t.me/BotFather).

5 - Fill `.env` file based on this help:

| Env Key               | Value                                                              |
|:----------------------|--------------------------------------------------------------------|
| INSTAGRAM_PROXY_LINK  | [Optional] HTTP proxy link                                         |
| INSTAGRAM_PROXY_USE   | True / False                                                       |
| TELEGRAM_BOT_USERNAME | Your telegram bot username                                         |
| TELEGRAM_BOT_TOKEN    | Your telegram bot token                                            |
| TELEGRAM_SUDO_IDS     | Comma-separated sudo IDs - [See your ID](https://t.me/userinfobot) |
| TELEGRAM_LOG_CHANNEL  | Your Telegram channel ID                                           |
| TELEGRAM_API_ID       | Your Telegram api id                                               |
| TELEGRAM_API_HASH     | Your Telegram api hash                                             |

## ▶️ Run
### You can run this app in two ways:

### 1 - With Docker:
```bash
docker-compose up --build -d
```
### 2 - Manual:
- Install dependencies:
```bash
pip install -r requirements.txt
```
- Run
```bash
python main.py
```

## 🔠 Commands
This bot will only answer to `TELEGRAM_SUDO_IDS`

To interact with the bot, open a chat with you Telegram Bot and start chatting:

| Command 	                          | Description 	                                                                  | Examples 	                             |
|------------------------------------|--------------------------------------------------------------------------------|----------------------------------------|
| /inspectors                        | List of all inspectors                                                         | /inspectors                            |
| /inspected_users                   | List of all inspected users                                                    | /inspected_users                       |
| /add_inspector USER PASS [2FACode] | Add new inspector                                                              | /add_inspector user_name MyPaSs 123456 |
| /relogin USER PASS [2FACode]       | Force re-login to inspector                                                    | /relogin user_name MyPaSs 123456       |                             |                                        |
| /del_inspector                     | Delete an inspector                                                            | /del_inspector                         |
| /inspect USERNAME                  | Add a user to inspect                                                          | /inspect user_name                     |
| /prune                             | Cleanup database from orphan inspected users and their follower/following list | /prune                                 |

➖➖➖➖
### \>> Don't Forget to give a ⭐️ !