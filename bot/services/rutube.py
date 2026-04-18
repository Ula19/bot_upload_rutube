"""Сервис скачивания видео с Rutube через yt-dlp.
Rutube может быть гео-ограничен вне РФ — fallback-цепочка обязательна:
direct → SOCKS5 (если задан) → WARP.
"""
import asyncio
import logging
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from bot.config import settings

logger = logging.getLogger(__name__)

# лимит файла (Local Bot API — 2 ГБ)
MAX_FILE_SIZE = settings.max_file_size

# WARP SOCKS5 прокси (контейнер warp в docker-compose)
WARP_PROXY = "socks5://warp:9091"

# рабочая директория для скачанных файлов
DOWNLOAD_DIR = "/tmp/rutube_bot"


@dataclass
class VideoInfo:
    """Информация о видео (до скачивания)"""
    title: str
    duration: int  # в секундах
    thumbnail: str | None = None
    uploader: str | None = None
    # доступные качества: {"360": 30, "720": 100} (качество -> примерный размер в МБ)
    qualities: dict | None = None
    is_live: bool = False


@dataclass
class DownloadResult:
    """Результат скачивания"""
    file_path: str
    media_type: str       # video или audio
    title: str
    duration: int | None = None
    width: int | None = None
    height: int | None = None
    format_key: str = ""  # video_360, video_720, audio


# тип для callback прогресса: (скачано_мб, всего_мб, процент)
ProgressCallback = Callable[[float, float, int], None] | None


class FileTooLargeError(Exception):
    """Файл превышает лимит Telegram (2 ГБ) и не может быть сплитнут (аудио)"""
    pass


def classify_error(error_msg: str) -> str:
    """Классифицирует ошибку yt-dlp в категорию.
    Возвращает: 'paid', 'geo_blocked', 'drm', 'private', 'not_found', 'network', 'unavailable', 'unknown'.
    """
    msg = error_msg.lower()

    # платный/подписочный контент: Rutube возвращает 404 на options JSON
    if "options" in msg and "404" in msg:
        return "paid"
    if "geo" in msg or "country" in msg or "region" in msg:
        return "geo_blocked"
    if "drm" in msg or "widevine" in msg:
        return "drm"
    if "private" in msg or "login required" in msg:
        return "private"
    if "not found" in msg or "404" in msg or "does not exist" in msg:
        return "not_found"
    if "timeout" in msg or "connection" in msg or "unreachable" in msg:
        return "network"
    if "unavailable" in msg or "not available" in msg:
        return "unavailable"

    return "unknown"


class RutubeDownloader:
    """Скачивает видео с Rutube через yt-dlp.
    Fallback chain: direct → SOCKS5 (если задан) → WARP.
    """

    def __init__(self):
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        self.download_dir = DOWNLOAD_DIR
        # callback для уведомления админа при ошибках
        self.on_source_failed: Callable[[str, str], None] | None = None

        # резидентный SOCKS5 прокси из настроек (опциональный)
        self._socks5_proxy = settings.socks5_proxy or None

        logger.info("RutubeDownloader инициализирован, dir=%s", self.download_dir)
        if self._socks5_proxy:
            logger.info("SOCKS5 прокси: настроен (fallback)")
        logger.info("WARP прокси: %s", WARP_PROXY)

    def _fire_source_failed(self, source: str, error: Exception) -> None:
        """Триггер callback'а о падении источника."""
        if self.on_source_failed is None:
            return
        try:
            self.on_source_failed(source, str(error))
        except Exception as e:
            logger.warning("on_source_failed callback упал: %s", e)

    def _cleanup_old_files(self, max_age_minutes: int = 30) -> None:
        """Чистит старые файлы из рабочей директории"""
        now = time.time()
        cutoff = now - max_age_minutes * 60
        try:
            for filename in os.listdir(self.download_dir):
                filepath = os.path.join(self.download_dir, filename)
                if os.path.isfile(filepath) and os.path.getmtime(filepath) < cutoff:
                    os.remove(filepath)
                    logger.info("Очистка старого файла: %s", filename)
        except OSError as e:
            logger.warning("Ошибка при очистке: %s", e)

    # === Настройки прокси ===

    def _base_opts(self) -> dict:
        """Базовые настройки yt-dlp (без прокси — прямое подключение)"""
        return {
            "quiet": True,
            "no_warnings": True,
            "socket_timeout": 30,
            "retries": 5,              # ретраи скачивания фрагментов HLS
            "fragment_retries": 5,     # ретраи отдельных фрагментов при сбое
            "extractor_retries": 3,    # ретраи API-вызовов (options/video JSON)
        }

    def _warp_opts(self) -> dict:
        """Настройки через WARP прокси"""
        return {
            **self._base_opts(),
            "proxy": WARP_PROXY,
        }

    def _socks5_opts(self) -> dict:
        """Настройки через резидентный SOCKS5 прокси"""
        return {
            **self._base_opts(),
            "proxy": self._socks5_proxy,
        }

    def _build_source_chain(self) -> list[tuple[str, dict]]:
        """Строит цепочку fallback источников: direct → SOCKS5 (если задан) → WARP."""
        chain = [("direct", self._base_opts())]
        if self._socks5_proxy:
            chain.append(("socks5", self._socks5_opts()))
        chain.append(("warp", self._warp_opts()))
        return chain

    # === Получение информации ===

    async def get_info(self, url: str) -> VideoInfo:
        """Получает метаданные видео. Fallback chain: direct → SOCKS5 → WARP."""
        t_start = time.monotonic()
        chain = self._build_source_chain()
        last_error = None

        for source_name, opts in chain:
            ydl_opts = {
                **opts,
                "skip_download": True,
                "ignore_no_formats_error": True,
            }

            loop = asyncio.get_running_loop()
            try:
                info = await loop.run_in_executor(
                    None, self._extract_info, url, ydl_opts
                )
                elapsed = time.monotonic() - t_start
                logger.info("[METRIC] get_info %.2fs source=%s url=%s", elapsed, source_name, url)

                qualities = self._parse_qualities(info)
                return VideoInfo(
                    title=info.get("title", "Без названия"),
                    duration=info.get("duration", 0) or 0,
                    thumbnail=info.get("thumbnail"),
                    uploader=info.get("uploader"),
                    qualities=qualities,
                    is_live=bool(info.get("is_live")),
                )

            except Exception as e:
                category = classify_error(str(e))
                # ошибки контента не решаются через fallback
                if category in ("not_found", "private", "drm", "paid"):
                    raise
                logger.warning("get_info через %s не удалось: %s", source_name, e)
                if category not in ("unavailable", "geo_blocked"):
                    self._fire_source_failed(source_name, e)
                last_error = e

        raise last_error

    # === Скачивание видео ===

    async def download_video(
        self, url: str, quality: str = "720",
        progress_callback: ProgressCallback = None,
    ) -> DownloadResult:
        """Скачивает видео. Fallback chain: direct → SOCKS5 → WARP."""
        self._cleanup_old_files()
        t_start = time.monotonic()
        chain = self._build_source_chain()
        last_error = None

        for source_name, opts in chain:
            try:
                result = await self._download_with_quality(
                    url, quality, progress_callback, opts=opts
                )
                self._log_download_metric("download_video", t_start, source_name, quality, result.file_path)
                return result
            except Exception as e:
                category = classify_error(str(e))
                if category in ("not_found", "private", "drm", "paid"):
                    raise
                logger.warning("download_video через %s не удалось: %s", source_name, e)
                if category not in ("unavailable", "geo_blocked"):
                    self._fire_source_failed(source_name, e)
                last_error = e

        raise last_error

    # === Скачивание аудио ===

    async def download_audio(
        self, url: str,
        progress_callback: ProgressCallback = None,
    ) -> DownloadResult:
        """Скачивает аудиодорожку. Fallback chain: direct → SOCKS5 → WARP."""
        self._cleanup_old_files()
        t_start = time.monotonic()
        chain = self._build_source_chain()
        last_error = None

        for source_name, opts in chain:
            try:
                result = await self._do_download_audio(url, progress_callback, opts=opts)
                self._log_download_metric("download_audio", t_start, source_name, "audio", result.file_path)
                return result
            except Exception as e:
                category = classify_error(str(e))
                if category in ("not_found", "private", "drm", "paid"):
                    raise
                logger.warning("download_audio через %s не удалось: %s", source_name, e)
                if category not in ("unavailable", "geo_blocked"):
                    self._fire_source_failed(source_name, e)
                last_error = e

        raise last_error

    # === Внутренние методы ===

    def _parse_qualities(self, info: dict) -> dict:
        """Парсит доступные качества из форматов yt-dlp.
        Качество = height (работает и для горизонтальных, и для вертикальных Shorts).
        Возвращает {height_str: size_mb}.
        """
        formats = info.get("formats", [])
        duration = info.get("duration", 0) or 0
        target_heights = [360, 480, 720, 1080, 1440, 2160]
        result = {}

        # оценка размера аудио-дорожки (если есть отдельный поток — для суммы с видео)
        audio_size = 0
        for fmt in formats:
            if fmt.get("vcodec", "none") != "none":
                continue
            if fmt.get("acodec", "none") == "none":
                continue
            size = fmt.get("filesize") or fmt.get("filesize_approx") or 0
            if not size and fmt.get("tbr") and duration:
                size = int(fmt["tbr"] * 1000 / 8 * duration)
            if size > audio_size:
                audio_size = size

        for h in target_heights:
            best_size = 0
            for fmt in formats:
                fmt_h = fmt.get("height") or 0
                if fmt_h != h:
                    continue
                if fmt.get("vcodec", "none") == "none":
                    continue
                size = fmt.get("filesize") or fmt.get("filesize_approx") or 0
                if not size and fmt.get("tbr") and duration:
                    size = int(fmt["tbr"] * 1000 / 8 * duration)
                if size > best_size:
                    best_size = size

            if best_size > 0:
                total = best_size + audio_size
                total_mb = int(total / 1024 / 1024)
                result[str(h)] = max(total_mb, 1)

        # если yt-dlp не вернул форматы по высоте — fallback на стандартные
        if not result:
            result = {"360": 0, "720": 0}

        return result

    async def _download_with_quality(
        self, url: str, quality: str,
        progress_callback: ProgressCallback = None,
        opts: dict = None,
    ) -> DownloadResult:
        """Скачивает видео в указанном качестве."""
        import yt_dlp

        output_template = os.path.join(self.download_dir, f"%(id)s_{quality}p.%(ext)s")
        height = int(quality)
        format_str = (
            f"bestvideo[height<={height}]+bestaudio"
            f"/best[height<={height}]"
            f"/best"
        )

        ydl_opts = {
            **opts,
            "format": format_str,
            "outtmpl": output_template,
            "merge_output_format": "mp4",
        }

        loop = asyncio.get_running_loop()
        info = await loop.run_in_executor(
            None, self._download, url, ydl_opts, progress_callback
        )

        file_path = self._find_downloaded_file(info, "mp4")
        if not file_path or not os.path.exists(file_path):
            raise RuntimeError("Не удалось найти скачанный видеофайл")

        return DownloadResult(
            file_path=file_path,
            media_type="video",
            title=info.get("title", "Rutube Video"),
            duration=info.get("duration"),
            width=info.get("width"),
            height=info.get("height"),
            format_key=f"video_{quality}",
        )

    async def _do_download_audio(
        self, url: str, progress_callback: ProgressCallback, opts: dict,
    ) -> DownloadResult:
        """Скачивает аудио. Rutube отдаёт HLS с вшитым аудио — все форматы combined.
        Берём САМЫЙ ЛЁГКИЙ combined-стрим (144p) и извлекаем из него аудио.
        Аудио-дорожка в HLS обычно одинакового качества во всех вариантах — AAC ~128kbps.
        """
        import yt_dlp

        output_template = os.path.join(self.download_dir, "%(id)s_audio.%(ext)s")
        ydl_opts = {
            **opts,
            # bestaudio если вдруг есть отдельный аудио-поток (редко),
            # иначе worst — самый лёгкий combined (144p, ~1-5МБ вместо 300МБ)
            "format": "bestaudio/worst",
            "outtmpl": output_template,
            # постпроцессор извлекает аудио в m4a; AAC копируется без re-encode
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "m4a",
            }],
        }

        loop = asyncio.get_running_loop()
        info = await loop.run_in_executor(
            None, self._download, url, ydl_opts, progress_callback
        )

        # после постпроцессора файл имеет расширение .m4a
        file_path = self._find_downloaded_file(info, "m4a")
        if not file_path or not os.path.exists(file_path):
            raise RuntimeError("Не удалось найти скачанный аудиофайл")

        # аудио обычно маленькое, но проверяем лимит
        file_size = os.path.getsize(file_path)
        if file_size > MAX_FILE_SIZE:
            self._remove_file(file_path)
            raise FileTooLargeError(
                f"Аудиофайл слишком большой ({file_size / 1024 / 1024:.0f} МБ)"
            )

        return DownloadResult(
            file_path=file_path,
            media_type="audio",
            title=info.get("title", "Rutube Audio"),
            duration=info.get("duration"),
            format_key="audio",
        )

    def _extract_info(self, url: str, opts: dict) -> dict:
        import yt_dlp
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(url, download=False)

    def _download(self, url: str, opts: dict, progress_callback: ProgressCallback = None) -> dict:
        import yt_dlp

        if progress_callback:
            last_update = {"time": 0}

            def _hook(d):
                if d["status"] != "downloading":
                    return
                now = time.time()
                if now - last_update["time"] < 3:
                    return
                last_update["time"] = now

                downloaded = d.get("downloaded_bytes", 0)
                total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
                if total > 0:
                    percent = int(downloaded / total * 100)
                    dl_mb = downloaded / 1024 / 1024
                    total_mb = total / 1024 / 1024
                    progress_callback(dl_mb, total_mb, percent)

            opts["progress_hooks"] = [_hook]

        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(url, download=True)

    def _find_downloaded_file(self, info: dict, expected_ext: str) -> str | None:
        """Ищет скачанный файл в рабочей директории по ID видео."""
        video_id = info.get("id", "")
        if not video_id:
            return None
        for filename in os.listdir(self.download_dir):
            if video_id in filename and filename.endswith(f".{expected_ext}"):
                return os.path.join(self.download_dir, filename)
        return None

    def _log_download_metric(
        self, op: str, t_start: float, source: str, quality: str, file_path: str,
    ) -> None:
        elapsed = time.monotonic() - t_start
        try:
            size_mb = os.path.getsize(file_path) / 1024 / 1024
        except OSError:
            size_mb = 0
        speed = size_mb / elapsed if elapsed > 0 else 0
        logger.info(
            "[METRIC] %s %.2fs source=%s quality=%s size=%.1fMB speed=%.1fMB/s",
            op, elapsed, source, quality, size_mb, speed,
        )

    def cleanup(self, result: DownloadResult) -> None:
        """Удаляет скачанный файл после отправки."""
        self._remove_file(result.file_path)

    def _remove_file(self, path: str) -> None:
        try:
            Path(path).unlink(missing_ok=True)
            logger.info("Удалён: %s", path)
        except OSError as e:
            logger.warning("Не удалось удалить файл: %s", e)


# глобальный экземпляр
downloader = RutubeDownloader()
