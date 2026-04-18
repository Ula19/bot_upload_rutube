"""Хэндлер скачивания — обрабатывает ссылки Rutube
Флоу: ссылка -> выбор формата -> выбор качества -> скачивание -> отправка
"""
import asyncio
import logging
import os
import time
from pathlib import Path

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, FSInputFile, Message

from bot.config import settings
from bot.database import async_session
from bot.database.crud import (
    get_cached_download,
    get_or_create_user,
    get_user_language,
    save_download,
)
from bot.emojis import E
from bot.i18n import t
from bot.keyboards.inline import (
    get_audio_suggest_keyboard,
    get_back_keyboard,
    get_format_keyboard,
    get_quality_keyboard,
)
from bot.services.rutube import FileTooLargeError, classify_error, downloader
from bot.utils.helpers import (
    clean_rutube_url,
    is_rutube_sport_url,
    is_rutube_url,
    resolve_rutube_sport_url,
)

logger = logging.getLogger(__name__)
router = Router()

# минимальный интервал обновления прогресса (Telegram лимит ~30 ред/мин)
PROGRESS_UPDATE_INTERVAL = 4

# порог для автосплита (чуть меньше 2 ГБ, с запасом)
SPLIT_THRESHOLD = 1.9 * 1024 * 1024 * 1024  # 1.9 ГБ

# максимум 10 одновременных скачиваний
_download_semaphore = asyncio.Semaphore(10)

# троттлинг алертов о fallback
_FALLBACK_ALERT_THROTTLE = 600  # 10 минут
_last_fallback_alert: dict[str, float] = {}

# категории которые не алертим админу — юзерские ошибки
_SILENT_CATEGORIES = {"unavailable", "not_found", "private", "geo_blocked", "drm", "paid"}

_ERROR_CATEGORY_LABELS = {
    "geo_blocked": "Гео-блокировка",
    "drm": "DRM-защита",
    "private": "Приватное видео",
    "not_found": "Видео не найдено",
    "network": "Сетевая ошибка",
    "unknown": "Неизвестная ошибка",
}


def _make_progress_bar(percent: int, dl_mb: float, total_mb: float, lang: str = "ru") -> str:
    """Рисует полоску прогресса"""
    filled = int(percent / 100 * 12)
    bar = "\u25b0" * filled + "\u25b1" * (12 - filled)
    return (
        f"{E['clock']} {t('download.downloading', lang)}\n"
        f"{bar} {percent}%\n"
        f"{dl_mb:.0f} МБ из {total_mb:.0f} МБ"
    )


# FSM для сохранения URL между шагами выбора
class DownloadStates(StatesGroup):
    waiting_format = State()
    waiting_quality = State()


@router.message(F.text)
async def handle_rutube_link(message: Message, state: FSMContext) -> None:
    """Обработка текстовых сообщений — ищем ссылки Rutube"""
    text = message.text.strip()

    async with async_session() as session:
        lang = await get_user_language(session, message.from_user.id)

    if not is_rutube_url(text):
        await message.answer(
            t("download.not_rutube", lang),
            parse_mode="HTML",
        )
        return

    clean_url = clean_rutube_url(text)

    status_msg = None
    try:
        status_msg = await message.answer(t("download.fetching_info", lang))

        # rutube.sport нужно отдельно: парсим страницу и достаём embed rutube.ru
        if is_rutube_sport_url(clean_url):
            resolved = await resolve_rutube_sport_url(clean_url)
            if not resolved:
                await status_msg.edit_text(
                    t("error.sport_no_embed", lang),
                    parse_mode="HTML",
                )
                return
            clean_url = resolved

        info = await downloader.get_info(clean_url)

        # прямой эфир не поддерживается
        if info.is_live:
            await status_msg.edit_text(
                t("error.live_stream", lang),
                parse_mode="HTML",
            )
            return

        # префлайт-фильтр: выкидываем качества с оценкой > лимита
        max_mb = settings.max_quality_size_mb
        filtered_qualities = {
            q: size for q, size in (info.qualities or {}).items()
            if size == 0 or size <= max_mb
        }

        # все качества слишком большие — предлагаем только аудио
        if info.qualities and not filtered_qualities:
            await state.set_state(DownloadStates.waiting_format)
            await state.update_data(url=clean_url)
            await status_msg.edit_text(
                t("error.too_large_suggest_audio", lang),
                reply_markup=get_audio_suggest_keyboard(lang),
                parse_mode="HTML",
            )
            return

        # сохраняем URL и инфо в FSM
        await state.set_state(DownloadStates.waiting_format)
        await state.update_data(
            url=clean_url,
            title=info.title,
            duration=info.duration,
            qualities=filtered_qualities,
        )

        duration_str = _format_duration(info.duration)

        await status_msg.edit_text(
            t("download.info", lang,
              title=info.title,
              duration=duration_str,
              uploader=info.uploader or "\u2014"),
            reply_markup=get_format_keyboard(lang),
            parse_mode="HTML",
        )

    except Exception as e:
        logger.error("Ошибка получения инфо: %s", e)
        error_text = _get_error_text(str(e), lang)
        if status_msg:
            await status_msg.edit_text(error_text, parse_mode="HTML")
        else:
            await message.answer(error_text, parse_mode="HTML")


@router.callback_query(F.data == "fmt_video")
async def choose_video_format(callback: CallbackQuery, state: FSMContext) -> None:
    """Юзер выбрал видео — показываем качество с размерами"""
    async with async_session() as session:
        lang = await get_user_language(session, callback.from_user.id)

    data = await state.get_data()
    qualities = data.get("qualities")
    await state.set_state(DownloadStates.waiting_quality)

    await callback.message.edit_text(
        t("download.choose_quality", lang),
        reply_markup=get_quality_keyboard(lang, qualities),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "fmt_audio")
async def download_audio(callback: CallbackQuery, state: FSMContext) -> None:
    """Юзер выбрал аудио — скачиваем"""
    data = await state.get_data()
    url = data.get("url")
    await state.clear()

    await callback.answer()

    async with async_session() as session:
        lang = await get_user_language(session, callback.from_user.id)

    if not url:
        await callback.message.answer(f"{E['cross']} {t('error.url_expired', lang)}")
        return

    await _process_download(
        callback.message, url, "audio", callback.from_user, lang, state
    )


@router.callback_query(F.data.startswith("quality_"))
async def choose_quality(callback: CallbackQuery, state: FSMContext) -> None:
    """Юзер выбрал качество — скачиваем видео"""
    quality = callback.data.replace("quality_", "")
    data = await state.get_data()
    url = data.get("url")
    qualities = data.get("qualities") or {}
    await state.clear()

    await callback.answer()

    async with async_session() as session:
        lang = await get_user_language(session, callback.from_user.id)

    if not url:
        await callback.message.answer(f"{E['cross']} {t('error.url_expired', lang)}")
        return

    format_key = f"video_{quality}"
    await _process_download(
        callback.message, url, format_key, callback.from_user, lang, state,
        qualities=qualities,
    )


async def _process_download(
    message: Message,
    url: str,
    format_key: str,
    user,
    lang: str = "ru",
    state: FSMContext | None = None,
    qualities: dict | None = None,
) -> None:
    """Скачивает и отправляет медиа."""
    # проверяем кэш
    async with async_session() as session:
        await get_or_create_user(
            session=session,
            telegram_id=user.id,
            username=user.username,
            full_name=user.full_name,
        )
        cached = await get_cached_download(session, url, format_key)

    if cached:
        logger.info("Кэш найден для %s [%s]", url, format_key)
        await _send_cached(message, cached.file_id, cached.media_type, lang)
        return

    async with _download_semaphore:
        status_msg = await message.edit_text(t("download.processing", lang))

        # callback для обновления прогресса
        last_progress_update = {"time": 0}
        loop = asyncio.get_running_loop()

        def on_progress(dl_mb: float, total_mb: float, percent: int):
            now = time.time()
            if now - last_progress_update["time"] < PROGRESS_UPDATE_INTERVAL:
                return
            last_progress_update["time"] = now

            text = _make_progress_bar(percent, dl_mb, total_mb, lang)
            try:
                asyncio.run_coroutine_threadsafe(
                    _safe_edit(status_msg, text), loop
                )
            except Exception:
                pass

        result = None
        split_parts = []
        try:
            if format_key == "audio":
                result = await downloader.download_audio(url, on_progress)
            else:
                quality = format_key.replace("video_", "")
                result = await downloader.download_video(url, quality, on_progress)

            # автосплит: если файл > 1.9 ГБ — режем на куски
            file_size = os.path.getsize(result.file_path)
            if file_size > SPLIT_THRESHOLD and result.media_type == "video":
                split_parts = await _split_video(result.file_path, SPLIT_THRESHOLD)
                if split_parts:
                    await _send_split_parts(message, split_parts, result, status_msg, lang)
                    # кэш не сохраняем для сплитнутых файлов (несколько file_id)
                    # инкрементим счётчик скачиваний
                    async with async_session() as session:
                        user_obj = await get_or_create_user(
                            session=session,
                            telegram_id=user.id,
                            username=user.username,
                            full_name=user.full_name,
                        )
                        user_obj.download_count += 1
                        await session.commit()
                    try:
                        await status_msg.delete()
                    except Exception:
                        pass
                    return

            file_id = await _send_media(message, result, status_msg, lang)

            # сохраняем в кэш
            if file_id:
                actual_format_key = result.format_key or format_key
                async with async_session() as session:
                    await save_download(
                        session=session,
                        source_url=url,
                        format_key=actual_format_key,
                        file_id=file_id,
                        media_type=result.media_type,
                    )
                    user_obj = await get_or_create_user(
                        session=session,
                        telegram_id=user.id,
                        username=user.username,
                        full_name=user.full_name,
                    )
                    user_obj.download_count += 1
                    await session.commit()

            try:
                await status_msg.delete()
            except Exception:
                pass

        except FileTooLargeError:
            # предлагаем качества пониже
            current_quality = format_key.replace("video_", "") if format_key.startswith("video_") else None
            lower_qualities = {}
            if current_quality and qualities:
                try:
                    current_h = int(current_quality)
                    lower_qualities = {
                        q: size for q, size in qualities.items()
                        if int(q) < current_h
                    }
                except ValueError:
                    pass

            if lower_qualities:
                await status_msg.edit_text(
                    t("error.too_large_try_lower", lang),
                    reply_markup=get_quality_keyboard(lang, lower_qualities),
                    parse_mode="HTML",
                )
                if state:
                    await state.set_state(DownloadStates.waiting_quality)
                    await state.update_data(url=url, qualities=lower_qualities)
            else:
                await status_msg.edit_text(
                    t("error.too_large_suggest_audio", lang),
                    reply_markup=get_audio_suggest_keyboard(lang),
                    parse_mode="HTML",
                )
                if state:
                    await state.set_state(DownloadStates.waiting_format)
                    await state.update_data(url=url)

        except Exception as e:
            logger.error("Ошибка скачивания %s: %s", url, e)
            error_text = _get_error_text(str(e), lang)
            try:
                await status_msg.edit_text(error_text, parse_mode="HTML")
            except Exception:
                await message.answer(error_text, parse_mode="HTML")

        finally:
            # обязательная очистка файлов
            if result:
                downloader.cleanup(result)
            # удаляем все части сплита
            for part_path in split_parts:
                Path(part_path).unlink(missing_ok=True)


async def _split_video(file_path: str, chunk_size: float) -> list[str]:
    """Разрезает видео на куски ~chunk_size через ffmpeg -c copy.
    Возвращает список путей к частям.
    """
    file_size = os.path.getsize(file_path)
    if file_size <= chunk_size:
        return []

    # вычисляем длительность видео
    try:
        probe = await asyncio.create_subprocess_exec(
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", file_path,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await asyncio.wait_for(probe.communicate(), timeout=30)
        total_duration = float(stdout.decode().strip())
    except Exception as e:
        logger.warning("Не удалось определить длительность для сплита: %s", e)
        return []

    # сколько частей нужно
    num_parts = int(file_size / chunk_size) + 1
    segment_duration = total_duration / num_parts

    parts = []
    base_path = Path(file_path)
    for i in range(num_parts):
        start = i * segment_duration
        part_path = str(base_path.parent / f"{base_path.stem}_part{i + 1}{base_path.suffix}")

        cmd = [
            "ffmpeg", "-y",
            "-ss", str(start),
            "-t", str(segment_duration),
            "-i", file_path,
            "-c", "copy",
            "-avoid_negative_ts", "make_zero",
            part_path,
        ]

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL,
            )
            await asyncio.wait_for(proc.wait(), timeout=300)
            if os.path.exists(part_path) and os.path.getsize(part_path) > 0:
                parts.append(part_path)
            else:
                logger.warning("Часть %d пустая или не создана", i + 1)
        except Exception as e:
            logger.error("Ошибка сплита части %d: %s", i + 1, e)

    return parts


async def _send_split_parts(
    message: Message, parts: list[str], result, status_msg, lang: str,
) -> None:
    """Отправляет части сплита серией."""
    total = len(parts)
    for i, part_path in enumerate(parts, 1):
        try:
            await status_msg.edit_text(
                t("download.uploading", lang) + f"\n\n{t('download.split_part', lang, current=i, total=total)}",
            )
        except Exception:
            pass

        file = FSInputFile(part_path)
        promo = t("download.promo", lang, bot_username=settings.bot_username)
        caption = f"{E['video']} {result.title} ({t('download.split_part', lang, current=i, total=total)}){promo}"

        await message.answer_video(
            video=file,
            caption=caption,
            duration=int(result.duration / total) if result.duration else None,
            width=result.width,
            height=result.height,
        )


async def _send_media(message: Message, result, status_msg=None, lang="ru") -> str | None:
    """Отправляет медиа юзеру и возвращает file_id."""
    file = FSInputFile(result.file_path)

    if status_msg:
        try:
            await status_msg.edit_text(t("download.uploading", lang))
        except Exception:
            pass

    t_upload = time.monotonic()
    try:
        size_mb = os.path.getsize(result.file_path) / 1024 / 1024
    except OSError:
        size_mb = 0

    if result.media_type == "video":
        promo = t("download.promo", lang, bot_username=settings.bot_username)
        sent = await message.answer_video(
            video=file,
            caption=f"{E['video']} {result.title}{promo}",
            duration=int(result.duration) if result.duration else None,
            width=result.width,
            height=result.height,
        )
        _log_upload_metric("video", t_upload, size_mb)
        return sent.video.file_id

    elif result.media_type == "audio":
        promo = t("download.promo", lang, bot_username=settings.bot_username)
        sent = await message.answer_audio(
            audio=file,
            caption=f"{E['audio']} {result.title}{promo}",
            duration=int(result.duration) if result.duration else None,
            title=result.title,
        )
        _log_upload_metric("audio", t_upload, size_mb)
        return sent.audio.file_id

    return None


def _log_upload_metric(media_type: str, t_start: float, size_mb: float) -> None:
    elapsed = time.monotonic() - t_start
    speed = size_mb / elapsed if elapsed > 0 else 0
    logger.info(
        "[METRIC] upload_%s %.2fs size=%.1fMB speed=%.1fMB/s",
        media_type, elapsed, size_mb, speed,
    )


async def _send_cached(
    message: Message, file_id: str, media_type: str, lang: str = "ru"
) -> None:
    """Отправляет из кэша по file_id"""
    try:
        promo = t("download.promo", lang, bot_username=settings.bot_username)
        if media_type == "video":
            await message.answer_video(video=file_id, caption=f"{E['video']} Rutube Video{promo}")
        elif media_type == "audio":
            await message.answer_audio(audio=file_id, caption=f"{E['audio']} Rutube Audio{promo}")
    except Exception as e:
        logger.error("Ошибка отправки из кэша: %s", e)
        await message.answer(f"{E['warning']} {t('error.cache_expired', lang)}")


async def _safe_edit(msg: Message, text: str) -> None:
    """Безопасно обновляет сообщение"""
    try:
        await msg.edit_text(text)
    except Exception:
        pass


def _format_duration(seconds: int) -> str:
    """Форматирует секунды в MM:SS или HH:MM:SS"""
    if not seconds:
        return "\u2014"
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def _get_error_text(error: str, lang: str = "ru") -> str:
    """Человеко-понятное сообщение об ошибке через classify_error"""
    category = classify_error(error)

    if category == "paid":
        return t("error.paid", lang)
    elif category == "geo_blocked":
        return t("error.geo_blocked", lang)
    elif category == "drm":
        return t("error.unavailable", lang)
    elif category == "private":
        return t("error.private", lang)
    elif category == "not_found":
        return t("error.not_found", lang)
    elif category == "network":
        return t("error.timeout", lang)
    elif category == "unavailable":
        return t("error.unavailable", lang)
    else:
        return t("error.generic", lang)


# bot instance — устанавливается из main.py через setup_fallback_alerts
_bot_ref = None
_event_loop = None


def setup_fallback_alerts(bot) -> None:
    """Подключает callback алертов админу к downloader."""
    global _bot_ref, _event_loop
    _bot_ref = bot
    _event_loop = asyncio.get_running_loop()
    downloader.on_source_failed = _on_source_failed
    logger.info("Алерты о падении источников подключены")


def _on_source_failed(source: str, error: str) -> None:
    """Sync callback — шедулит асинхронную отправку алерта."""
    if _bot_ref is None or _event_loop is None:
        return
    try:
        asyncio.run_coroutine_threadsafe(_send_fallback_alert(source, error), _event_loop)
    except RuntimeError:
        pass


async def _send_fallback_alert(source: str, error: str) -> None:
    """Отправляет алерт админу о проблеме. С троттлингом и классификацией."""
    now = time.time()
    category = classify_error(error)

    if category in _SILENT_CATEGORIES:
        return

    throttle_key = f"{source}:{category}"
    last = _last_fallback_alert.get(throttle_key, 0)
    if now - last < _FALLBACK_ALERT_THROTTLE:
        return
    _last_fallback_alert[throttle_key] = now

    short_error = error[:300] + "..." if len(error) > 300 else error
    category_label = _ERROR_CATEGORY_LABELS.get(category, category)

    text = (
        f"{E['warning']} <b>Ошибка скачивания Rutube!</b>\n\n"
        f"<b>Источник:</b> {source}\n"
        f"<b>Категория:</b> {category_label}\n"
        f"<b>Ошибка:</b> <code>{short_error}</code>"
    )

    for admin_id in settings.admin_id_list:
        try:
            await _bot_ref.send_message(admin_id, text, parse_mode="HTML")
            logger.info("Админ %s уведомлён о проблеме %s (%s)", admin_id, source, category)
        except Exception as e:
            logger.warning("Не удалось уведомить админа %s: %s", admin_id, e)
