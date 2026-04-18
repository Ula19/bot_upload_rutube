# bot_4_rutube

Telegram-бот для скачивания видео с Rutube. Отправь ссылку — получи файл прямо в Telegram.

## Стек

- Python 3.12 + aiogram 3.x
- PostgreSQL + SQLAlchemy async
- yt-dlp + deno + ffmpeg
- Cloudflare WARP + резидентный прокси
- Docker Compose

## Быстрый старт

```bash
cp .env.example .env
# заполни BOT_TOKEN, API_ID, API_HASH, ADMIN_IDS, DB_PASSWORD
docker compose up -d --build
```

## Структура

```
bot/
├── main.py              # entrypoint
├── config.py            # настройки из .env
├── i18n.py              # ru / uz / en переводы
├── handlers/            # хендлеры команд
├── middlewares/         # подписка, rate limit
├── keyboards/           # inline-клавиатуры
├── services/            # сервис скачивания (TODO)
├── database/            # модели и CRUD
└── utils/               # helpers, commands
```

## Переменные окружения

| Переменная | Описание |
|---|---|
| `BOT_TOKEN` | Токен от @BotFather |
| `API_ID` / `API_HASH` | Telegram API для Local Bot API |
| `ADMIN_IDS` | ID админов через запятую |
| `DB_PASSWORD` | Пароль PostgreSQL |
| `PROXY_URL` | SOCKS5 прокси (primary) |
| `SOCKS5_PROXY` | SOCKS5 прокси (резервный / цепочка) |
