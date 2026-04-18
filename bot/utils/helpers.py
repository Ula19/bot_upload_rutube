"""Утилиты и вспомогательные функции"""
import asyncio
import logging
import re
import urllib.request

logger = logging.getLogger(__name__)


# паттерны Rutube ссылок — все поддерживаемые типы (rutube.ru и rutube.sport)
_RUTUBE_PATTERNS = [
    r"https?://(www\.)?rutube\.ru/video/[\w\-]+",
    r"https?://(www\.)?rutube\.ru/play/embed/[\w\-]+",
    r"https?://(www\.)?rutube\.ru/shorts/[\w\-]+",
    r"https?://(www\.)?rutube\.ru/live/video/[\w\-]+",
    r"https?://(www\.)?rutube\.ru/channel/[\w\-]+/video/[\w\-]+",
    # rutube.sport — отдельный домен, через embed-резолвер
    r"https?://(www\.)?rutube\.sport/video/[\w\-]+",
    r"https?://(www\.)?rutube\.sport/stream/[\w\-]+",
]


def is_rutube_url(text: str) -> bool:
    """Проверяет, является ли текст ссылкой на Rutube"""
    text = text.strip()
    return any(re.match(pattern, text) for pattern in _RUTUBE_PATTERNS)


def is_rutube_sport_url(url: str) -> bool:
    """Проверяет, это ли rutube.sport ссылка (нужен резолвер в embed)"""
    return bool(re.match(r"https?://(www\.)?rutube\.sport/", url.strip()))


def clean_rutube_url(url: str) -> str:
    """Очищает URL — убирает лишние query-параметры, нормализует"""
    url = url.strip()

    # rutube.sport оставляем как есть — его обработает resolve_rutube_sport_url
    if is_rutube_sport_url(url):
        return url.split("?")[0].rstrip("/") + "/"

    # rutube.ru/video/<id>/ — убираем query params
    for pattern in [
        r"(rutube\.ru/video/[\w\-]+)",
        r"(rutube\.ru/shorts/[\w\-]+)",
        r"(rutube\.ru/live/video/[\w\-]+)",
        r"(rutube\.ru/channel/[\w\-]+/video/[\w\-]+)",
        r"(rutube\.ru/play/embed/[\w\-]+)",
    ]:
        match = re.search(pattern, url)
        if match:
            return f"https://{match.group(1)}/"

    # fallback — просто убираем query
    return url.split("?")[0].rstrip("/") + "/"


def extract_rutube_id(url: str) -> str | None:
    """Извлекает video ID из Rutube URL"""
    patterns = [
        r"rutube\.ru/video/([\w\-]+)",
        r"rutube\.ru/play/embed/([\w\-]+)",
        r"rutube\.ru/shorts/([\w\-]+)",
        r"rutube\.ru/live/video/([\w\-]+)",
        r"rutube\.ru/channel/[\w\-]+/video/([\w\-]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


async def resolve_rutube_sport_url(url: str, timeout: int = 10) -> str | None:
    """Парсит rutube.sport страницу и извлекает embed-ссылку rutube.ru.
    Возвращает https://rutube.ru/play/embed/<id>/ или None если embed не найден.
    """
    loop = asyncio.get_running_loop()
    try:
        html = await loop.run_in_executor(None, _fetch_html, url, timeout)
    except Exception as e:
        logger.warning("Не удалось получить страницу %s: %s", url, e)
        return None

    match = re.search(r"rutube\.ru/play/embed/([\w\-]+)", html)
    if not match:
        logger.warning("На странице %s не найден embed rutube.ru", url)
        return None

    return f"https://rutube.ru/play/embed/{match.group(1)}/"


def _fetch_html(url: str, timeout: int) -> str:
    """Синхронная загрузка HTML (для run_in_executor)"""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="ignore")
