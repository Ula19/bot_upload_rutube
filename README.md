# bot_4_rutube

Telegram-бот для скачивания видео с Rutube. Отправь ссылку — получи файл прямо в Telegram.

## Что умеет

- Качает **видео** с выбором качества (360p/480p/720p/1080p/1440p/2160p — что отдаст Rutube)
- Качает **аудио** (m4a, извлечение из HLS через ffmpeg)
- Поддерживает обычные видео, **Shorts**, записи эфиров, видео из каналов
- Отдельно `rutube.sport/video/...` — через резолвер embed'а в `rutube.ru`
- **Автосплит** файлов > 1.9 ГБ на части ~1.9 ГБ (`ffmpeg -c copy`, без перекодирования)
- **Кэш file_id** в PostgreSQL — повторная отправка той же ссылки мгновенная
- Префлайт-фильтр: качества с предполагаемым размером > лимита не показываются юзеру
- Админ-панель: статистика, обязательная подписка на каналы, массовая рассылка
- Мультиязычность: `ru` / `uz` / `en`
- Rate limit: 5 запросов/мин на юзера

## Что НЕ поддерживается

- Прямые эфиры в реальном времени (бот ответит "трансляции не поддерживаются")
- Скачивание всего канала / плейлиста одной ссылкой
- Платный контент по подписке Rutube (бот ответит "контент по подписке")

## Стек

- Python 3.12 + aiogram 3.x
- PostgreSQL + SQLAlchemy async
- yt-dlp (зафиксирован на конкретную версию) + ffmpeg + deno
- Cloudflare WARP (Docker) + опциональный резидентный SOCKS5
- Local Bot API (контейнер `aiogram/telegram-bot-api`) — файлы до 2 ГБ
- Docker Compose

## Fallback-цепочка скачивания

```
direct  →  SOCKS5 (если задан в .env)  →  WARP
```

Контентные ошибки (`not_found` / `private` / `drm` / `paid`) сразу пробрасываются без перебора — смена прокси им всё равно не поможет. Сетевые/гео-ошибки переходят к следующему источнику.

## Быстрый старт

```bash
cp .env.example .env
# заполни BOT_TOKEN, API_ID, API_HASH, ADMIN_IDS, DB_PASSWORD
docker compose up -d --build
```

## Переменные окружения

| Переменная | Обязательная | Описание |
|---|---|---|
| `BOT_TOKEN` | ✅ | Токен от @BotFather |
| `API_ID` / `API_HASH` | ✅ | Telegram API для Local Bot API (https://my.telegram.org) |
| `BOT_USERNAME` | ✅ | Юзернейм бота (без @) — для рекламной подписи |
| `ADMIN_IDS` | ✅ | Telegram ID админов через запятую |
| `ADMIN_USERNAME` |  | Юзернейм админа для связи (в `/help`) |
| `DB_PASSWORD` | ✅ | Пароль PostgreSQL |
| `DB_NAME` / `DB_USER` / `DB_HOST` / `DB_PORT` |  | Параметры БД (по умолчанию `bot_4_rutube` / `postgres` / `postgres` / `5432`) |
| `SOCKS5_PROXY` |  | Резидентный SOCKS5 (`socks5://user:pass@host:port`). Если пустой — цепочка `direct → WARP` |
| `CACHE_TTL_DAYS` |  | Сколько дней хранить кэш file_id (по умолчанию 1) |
| `MAX_QUALITY_SIZE_MB` |  | Префлайт-фильтр: качества с оценкой > этого порога скрываются (по умолчанию 2000) |

## Команды бота

- `/start` — запуск, приветствие, главное меню
- `/menu` — главное меню
- `/profile` — профиль пользователя и счётчик скачиваний
- `/help` — помощь
- `/language` — сменить язык интерфейса
- `/admin` — админ-панель (только для `ADMIN_IDS`)

## Структура

```
bot/
├── main.py              # entrypoint, Local Bot API, фоновая очистка
├── config.py            # pydantic-settings, чтение .env
├── i18n.py              # переводы ru / uz / en
├── emojis.py            # премиум-эмодзи (E_ID для кнопок, E для текста)
├── database/
│   ├── models.py        # User, Channel, Download (кэш)
│   └── crud.py          # CRUD + функции кэша с TTL
├── handlers/
│   ├── start.py         # /start, меню, профиль, язык, подписка
│   ├── admin.py         # /admin: статистика, каналы, рассылка
│   └── download.py      # обработка ссылок, FSM, автосплит, отправка
├── middlewares/
│   ├── subscription.py  # обязательная подписка на каналы
│   └── rate_limit.py    # 5 запросов/мин на юзера
├── keyboards/
│   ├── inline.py        # меню, формат, качество, подписка, язык
│   └── admin.py         # админ-клавиатуры
├── services/
│   └── rutube.py        # RutubeDownloader — yt-dlp + fallback-цепочка
└── utils/
    ├── helpers.py       # парсер Rutube URL, резолвер rutube.sport
    └── commands.py      # установка меню команд Telegram на нужном языке
```

## Деплой

WARP может конфликтовать с Tailscale на локалке — на сервере без Tailscale работает штатно. Контейнер `autoheal` автоматически перезапускает WARP, если тот упадёт в unhealthy.

Фоновая задача внутри бота каждые 5 минут чистит:
- Протухшие записи кэша `Download` из БД
- Старые файлы из `/tmp/rutube_bot` (> 30 мин)
- Файлы Local Bot API в `/var/lib/telegram-bot-api` (> 1 часа)
