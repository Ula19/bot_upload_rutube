"""Мультиязычность — русский, узбекский, английский
Использование: from bot.i18n import t
  t("start.welcome", lang="en", name="John")
"""

from bot.emojis import E

TRANSLATIONS = {
    # === /start ===
    "start.welcome": {
        "ru": (
            f"{E['bot']} <b>Привет, {{name}}!</b>\n\n"
            f"{E['video']} Я помогу тебе скачать видео с Rutube.\n\n"
            f"{E['pin']} <b>Как пользоваться:</b>\n"
            "Просто отправь мне ссылку на видео — "
            f"и я скачаю его для тебя! {E['plane']}\n\n"
            "Выбери действие ниже:"
        ),
        "uz": (
            f"{E['bot']} <b>Salom, {{name}}!</b>\n\n"
            f"{E['video']} Rutube'dan video yuklab olishda yordam beraman.\n\n"
            f"{E['pin']} <b>Qanday foydalanish:</b>\n"
            "Menga video havolasini yuboring — "
            f"men sizga yuklab beraman! {E['plane']}\n\n"
            "Quyidagi tugmalardan birini tanlang:"
        ),
        "en": (
            f"{E['bot']} <b>Hello, {{name}}!</b>\n\n"
            f"{E['video']} I'll help you download videos from Rutube.\n\n"
            f"{E['pin']} <b>How to use:</b>\n"
            "Just send me a video link — "
            f"and I'll download it for you! {E['plane']}\n\n"
            "Choose an action below:"
        ),
    },

    # === Кнопки главного меню ===
    "btn.download": {
        "ru": "Скачать видео",
        "uz": "Video yuklab olish",
        "en": "Download video",
    },
    "btn.profile": {
        "ru": "Мой профиль",
        "uz": "Mening profilim",
        "en": "My profile",
    },
    "btn.help": {
        "ru": "Помощь",
        "uz": "Yordam",
        "en": "Help",
    },
    "btn.back": {
        "ru": "Назад",
        "uz": "Orqaga",
        "en": "Back",
    },
    "btn.language": {
        "ru": "Сменить язык",
        "uz": "Tilni o'zgartirish",
        "en": "Change language",
    },

    # === Кнопки формата и качества ===
    "btn.format_video": {
        "ru": "Видео (MP4)",
        "uz": "Video (MP4)",
        "en": "Video (MP4)",
    },
    "btn.format_audio": {
        "ru": "Аудио",
        "uz": "Audio",
        "en": "Audio",
    },
    "btn.download_audio_instead": {
        "ru": "Скачать аудио вместо видео",
        "uz": "Video o'rniga audio yuklab olish",
        "en": "Download audio instead",
    },

    # === Скачивание (TODO: адаптировать под Rutube) ===
    "download.prompt": {
        "ru": (
            f"{E['download']} <b>Скачивание с Rutube</b>\n\n"
            "Отправь мне ссылку на видео:\n\n"
            f"{E['link']} Пример: <code>https://rutube.ru/video/...</code>"
        ),
        "uz": (
            f"{E['download']} <b>Rutube'dan yuklab olish</b>\n\n"
            "Menga video havolasini yuboring:\n\n"
            f"{E['link']} Misol: <code>https://rutube.ru/video/...</code>"
        ),
        "en": (
            f"{E['download']} <b>Download from Rutube</b>\n\n"
            "Send me a video link:\n\n"
            f"{E['link']} Example: <code>https://rutube.ru/video/...</code>"
        ),
    },
    "download.fetching_info": {
        "ru": f"{E['search']} Получаю информацию о видео...",
        "uz": f"{E['search']} Video haqida ma'lumot olinmoqda...",
        "en": f"{E['search']} Fetching video info...",
    },
    "download.info": {
        "ru": (
            f"{E['camera']} <b>{{title}}</b>\n\n"
            f"{E['clock']} Длительность: {{duration}}\n"
            f"{E['profile']} Автор: {{uploader}}\n\n"
            "Выбери формат:"
        ),
        "uz": (
            f"{E['camera']} <b>{{title}}</b>\n\n"
            f"{E['clock']} Davomiyligi: {{duration}}\n"
            f"{E['profile']} Muallif: {{uploader}}\n\n"
            "Formatni tanlang:"
        ),
        "en": (
            f"{E['camera']} <b>{{title}}</b>\n\n"
            f"{E['clock']} Duration: {{duration}}\n"
            f"{E['profile']} Author: {{uploader}}\n\n"
            "Choose format:"
        ),
    },
    "download.choose_quality": {
        "ru": f"{E['camera']} <b>Выбери качество видео:</b>",
        "uz": f"{E['camera']} <b>Video sifatini tanlang:</b>",
        "en": f"{E['camera']} <b>Choose video quality:</b>",
    },
    "download.processing": {
        "ru": f"{E['clock']} Скачиваю... Подожди немного",
        "uz": f"{E['clock']} Yuklab olinmoqda... Biroz kuting",
        "en": f"{E['clock']} Downloading... Please wait",
    },
    "download.uploading": {
        "ru": f"{E['plane']} Почти готово! Загружаю файл в Telegram... Это займет пару минут {E['clock']}",
        "uz": f"{E['plane']} Deyarli tayyor! Fayl Telegramga yuklanmoqda... Bu bir necha daqiqa vaqt oladi {E['clock']}",
        "en": f"{E['plane']} Almost done! Uploading file to Telegram... This will take a couple of minutes {E['clock']}",
    },
    "download.not_rutube": {
        "ru": (
            f"{E['search']} Это не похоже на ссылку Rutube.\n\n"
            "Отправь ссылку вида:\n"
            "<code>https://rutube.ru/video/...</code>"
        ),
        "uz": (
            f"{E['search']} Bu Rutube havolasiga o'xshamaydi.\n\n"
            "Quyidagi ko'rinishdagi havolani yuboring:\n"
            "<code>https://rutube.ru/video/...</code>"
        ),
        "en": (
            f"{E['search']} This doesn't look like a Rutube link.\n\n"
            "Send a link like:\n"
            "<code>https://rutube.ru/video/...</code>"
        ),
    },
    "download.progress": {
        "ru": "{bar}\n{percent}% ({dl_mb:.0f} МБ из {total_mb:.0f} МБ)",
        "uz": "{bar}\n{percent}% ({dl_mb:.0f} MB dan {total_mb:.0f} MB)",
        "en": "{bar}\n{percent}% ({dl_mb:.0f} MB of {total_mb:.0f} MB)",
    },
    "download.split_part": {
        "ru": "Часть {current}/{total}",
        "uz": "{current}/{total} qism",
        "en": "Part {current}/{total}",
    },
    "download.downloading": {
        "ru": "Скачиваю...",
        "uz": "Yuklab olinmoqda...",
        "en": "Downloading...",
    },

    # === Профиль ===
    "profile.title": {
        "ru": (
            f"{E['profile']} <b>Твой профиль</b>\n\n"
            f"{E['edit']} Имя: {{full_name}}\n"
            f"{E['info']} ID: <code>{{user_id}}</code>\n"
            f"{E['download']} Скачиваний (всего): {{downloads}}\n"
        ),
        "uz": (
            f"{E['profile']} <b>Sizning profilingiz</b>\n\n"
            f"{E['edit']} Ism: {{full_name}}\n"
            f"{E['info']} ID: <code>{{user_id}}</code>\n"
            f"{E['download']} Yuklashlar (jami): {{downloads}}\n"
        ),
        "en": (
            f"{E['profile']} <b>Your profile</b>\n\n"
            f"{E['edit']} Name: {{full_name}}\n"
            f"{E['info']} ID: <code>{{user_id}}</code>\n"
            f"{E['download']} Downloads (total): {{downloads}}\n"
        ),
    },

    # === Помощь ===
    "help.text": {
        "ru": (
            f"{E['book']} <b>Помощь</b>\n\n"
            f"{E['star']} Отправь ссылку на Rutube видео — получишь файл\n"
            f"{E['star']} Поддерживаются: видео с rutube.ru\n"
            f"{E['star']} Можно скачать как видео или аудио\n"
            f"{E['lock']} Приватные видео не поддерживаются\n\n"
            f"{E['plane']} По вопросам: @{{admin_username}}"
        ),
        "uz": (
            f"{E['book']} <b>Yordam</b>\n\n"
            f"{E['star']} Rutube video havolasini yuboring — faylni olasiz\n"
            f"{E['star']} Qo'llab-quvvatlanadi: rutube.ru videolari\n"
            f"{E['star']} Video yoki audio sifatida yuklab olish mumkin\n"
            f"{E['lock']} Yopiq videolar qo'llab-quvvatlanmaydi\n\n"
            f"{E['plane']} Savollar uchun: @{{admin_username}}"
        ),
        "en": (
            f"{E['book']} <b>Help</b>\n\n"
            f"{E['star']} Send a Rutube video link — get the file\n"
            f"{E['star']} Supported: videos from rutube.ru\n"
            f"{E['star']} Download as video or audio\n"
            f"{E['lock']} Private videos are not supported\n\n"
            f"{E['plane']} Contact: @{{admin_username}}"
        ),
    },

    # === Подписка ===
    "sub.welcome": {
        "ru": (
            f"{E['bot']} <b>Привет!</b>\n\n"
            f"{E['video']} Этот бот скачивает видео и аудио "
            "с Rutube — быстро и бесплатно!\n\n"
            f"{E['lock']} <b>Для начала подпишись на каналы ниже:</b>\n\n"
            f"После подписки нажми «{E['check']} Проверить подписку»"
        ),
        "uz": (
            f"{E['bot']} <b>Salom!</b>\n\n"
            f"{E['video']} Bu bot Rutube'dan video va audio "
            "yuklab oladi — tez va bepul!\n\n"
            f"{E['lock']} <b>Boshlash uchun quyidagi kanallarga obuna bo'ling:</b>\n\n"
            f"Obuna bo'lgandan keyin «{E['check']} Obunani tekshirish» tugmasini bosing"
        ),
        "en": (
            f"{E['bot']} <b>Hello!</b>\n\n"
            f"{E['video']} This bot downloads videos and audio "
            "from Rutube — fast and free!\n\n"
            f"{E['lock']} <b>To start, subscribe to the channels below:</b>\n\n"
            f"After subscribing, tap «{E['check']} Check subscription»"
        ),
    },
    "sub.not_subscribed": {
        "ru": (
            f"{E['cross']} <b>Ты ещё не подписался на все каналы:</b>\n\n"
            f"Подпишись и нажми «{E['check']} Проверить подписку» ещё раз."
        ),
        "uz": (
            f"{E['cross']} <b>Siz hali barcha kanallarga obuna bo'lmadingiz:</b>\n\n"
            f"Obuna bo'ling va «{E['check']} Obunani tekshirish» tugmasini qayta bosing."
        ),
        "en": (
            f"{E['cross']} <b>You haven't subscribed to all channels yet:</b>\n\n"
            f"Subscribe and tap «{E['check']} Check subscription» again."
        ),
    },
    "sub.success": {
        "ru": (
            f"{E['check']} <b>Отлично, {{name}}!</b>\n\n"
            f"Теперь ты можешь пользоваться ботом! {E['plane']}\n\n"
            "Отправь ссылку на Rutube видео."
        ),
        "uz": (
            f"{E['check']} <b>Ajoyib, {{name}}!</b>\n\n"
            f"Endi siz botdan foydalanishingiz mumkin! {E['plane']}\n\n"
            "Rutube video havolasini yuboring."
        ),
        "en": (
            f"{E['check']} <b>Great, {{name}}!</b>\n\n"
            f"You can now use the bot! {E['plane']}\n\n"
            "Send a Rutube video link."
        ),
    },
    "btn.check_sub": {
        "ru": "Проверить подписку",
        "uz": "Obunani tekshirish",
        "en": "Check subscription",
    },
    "sub.check_alert_fail": {
        "ru": f"{E['cross']} Подпишись на все каналы!",
        "uz": f"{E['cross']} Barcha kanallarga obuna bo'ling!",
        "en": f"{E['cross']} Subscribe to all channels!",
    },
    "sub.check_alert_ok": {
        "ru": f"{E['check']} Подписка подтверждена!",
        "uz": f"{E['check']} Obuna tasdiqlandi!",
        "en": f"{E['check']} Subscription confirmed!",
    },
    "sub.not_required": {
        "ru": f"{E['check']} Подписка не требуется!",
        "uz": f"{E['check']} Obuna talab qilinmaydi!",
        "en": f"{E['check']} No subscription required!",
    },

    # === Ошибки ===
    "error.live_stream": {
        "ru": f"{E['warning']} <b>Прямой эфир</b>\n\nСкачивание прямых трансляций не поддерживается.",
        "uz": f"{E['warning']} <b>Jonli efir</b>\n\nJonli efirlarni yuklab olish qo'llab-quvvatlanmaydi.",
        "en": f"{E['warning']} <b>Live stream</b>\n\nDownloading live streams is not supported.",
    },
    "error.private": {
        "ru": f"{E['lock']} <b>Видео приватное</b>\n\nСкачивание приватных видео невозможно.",
        "uz": f"{E['lock']} <b>Video yopiq</b>\n\nYopiq videolarni yuklab olish mumkin emas.",
        "en": f"{E['lock']} <b>Private video</b>\n\nDownloading private videos is not possible.",
    },
    "error.paid": {
        "ru": f"{E['lock']} <b>Контент по подписке</b>\n\nВидео доступно только по платной подписке Rutube — скачать не получится.",
        "uz": f"{E['lock']} <b>Obunali kontent</b>\n\nVideo faqat Rutube pullik obunasi bilan ochiladi — yuklab olish mumkin emas.",
        "en": f"{E['lock']} <b>Subscription content</b>\n\nThis video requires a paid Rutube subscription — cannot be downloaded.",
    },
    "error.sport_no_embed": {
        "ru": f"{E['cross']} <b>Не удалось получить видео</b>\n\nНа странице rutube.sport не найден проигрыватель. Возможно, это прямой эфир или закрытый контент.",
        "uz": f"{E['cross']} <b>Video olinmadi</b>\n\nrutube.sport sahifasida pleyer topilmadi. Ehtimol bu jonli efir yoki yopiq kontent.",
        "en": f"{E['cross']} <b>Could not fetch video</b>\n\nNo player found on the rutube.sport page. It may be a live stream or restricted content.",
    },
    "error.not_found": {
        "ru": f"{E['cross']} <b>Видео не найдено</b>\n\nВозможно, оно удалено или ссылка неправильная.",
        "uz": f"{E['cross']} <b>Video topilmadi</b>\n\nEhtimol, u o'chirilgan yoki havola noto'g'ri.",
        "en": f"{E['cross']} <b>Video not found</b>\n\nIt may have been deleted or the link is incorrect.",
    },
    "error.unavailable": {
        "ru": f"{E['cross']} <b>Видео недоступно</b>\n\nВозможно, доступ ограничен.",
        "uz": f"{E['cross']} <b>Video mavjud emas</b>\n\nEhtimol, kirish cheklangan.",
        "en": f"{E['cross']} <b>Video unavailable</b>\n\nAccess may be restricted.",
    },
    "error.geo_blocked": {
        "ru": f"{E['cross']} <b>Видео заблокировано в вашем регионе</b>\n\nАвтор ограничил доступ к видео по географии.",
        "uz": f"{E['cross']} <b>Video sizning mintaqangizda bloklangan</b>\n\nMuallif videoga geografik cheklov qo'ygan.",
        "en": f"{E['cross']} <b>Video is geo-blocked</b>\n\nThe uploader has restricted this video by region.",
    },
    "error.too_large": {
        "ru": f"{E['package']} <b>Файл слишком большой</b>\n\nTelegram ограничивает размер файла до 2 ГБ.",
        "uz": f"{E['package']} <b>Fayl juda katta</b>\n\nTelegram fayl hajmini 2 GB bilan cheklaydi.",
        "en": f"{E['package']} <b>File too large</b>\n\nTelegram limits file size to 2 GB.",
    },
    "error.too_large_try_lower": {
        "ru": (
            f"{E['package']} <b>Видео слишком большое</b>\n\n"
            "Файл превысил лимит 2 ГБ. Попробуй качество пониже:"
        ),
        "uz": (
            f"{E['package']} <b>Video juda katta</b>\n\n"
            "Fayl 2 GB dan oshdi. Pastroq sifatni tanlang:"
        ),
        "en": (
            f"{E['package']} <b>Video too large</b>\n\n"
            "File exceeded 2 GB limit. Try a lower quality:"
        ),
    },
    "error.too_large_suggest_audio": {
        "ru": (
            f"{E['package']} <b>Видео слишком большое</b>\n\n"
            "Файл превышает лимит 2 ГБ даже в минимальном качестве.\n"
            "Попробуй скачать аудио:"
        ),
        "uz": (
            f"{E['package']} <b>Video juda katta</b>\n\n"
            "Fayl minimal sifatda ham 2 GB dan oshadi.\n"
            "Audio yuklab ko'ring:"
        ),
        "en": (
            f"{E['package']} <b>Video too large</b>\n\n"
            "File exceeds 2 GB even at minimum quality.\n"
            "Try downloading audio:"
        ),
    },
    "error.timeout": {
        "ru": f"{E['clock']} <b>Превышено время ожидания</b>\n\nПопробуй ещё раз через пару минут.",
        "uz": f"{E['clock']} <b>Kutish vaqti tugadi</b>\n\nBir necha daqiqadan keyin qayta urinib ko'ring.",
        "en": f"{E['clock']} <b>Request timed out</b>\n\nPlease try again in a few minutes.",
    },
    "error.generic": {
        "ru": f"{E['cross']} <b>Не удалось скачать</b>\n\nПопробуй позже или проверь ссылку.",
        "uz": f"{E['cross']} <b>Yuklab olib bo'lmadi</b>\n\nKeyinroq urinib ko'ring yoki havolani tekshiring.",
        "en": f"{E['cross']} <b>Download failed</b>\n\nTry again later or check the link.",
    },
    "error.rate_limit": {
        "ru": f"{E['clock']} <b>Слишком много запросов!</b>\n\nПодожди {{seconds}} секунд и попробуй снова.",
        "uz": f"{E['clock']} <b>Juda ko'p so'rovlar!</b>\n\n{{seconds}} soniya kuting va qayta urinib ko'ring.",
        "en": f"{E['clock']} <b>Too many requests!</b>\n\nWait {{seconds}} seconds and try again.",
    },
    "error.url_expired": {
        "ru": "Ссылка не найдена, отправь заново",
        "uz": "Havola topilmadi, qaytadan yuboring",
        "en": "Link not found, please send again",
    },
    "error.cache_expired": {
        "ru": "Кэш устарел. Отправь ссылку ещё раз.",
        "uz": "Kesh eskirgan. Havolani qayta yuboring.",
        "en": "Cache expired. Please send the link again.",
    },

    # === Выбор языка ===
    "lang.choose": {
        "ru": f"{E['gear']} <b>Выберите язык:</b>",
        "uz": f"{E['gear']} <b>Tilni tanlang:</b>",
        "en": f"{E['gear']} <b>Choose language:</b>",
    },
    "lang.changed": {
        "ru": f"{E['check']} Язык изменён на русский",
        "uz": f"{E['check']} Til o'zbek tiliga o'zgartirildi",
        "en": f"{E['check']} Language changed to English",
    },

    # === Админ-панель ===
    "admin.title": {
        "ru": f"{E['gear']} <b>Админ-панель</b>\n\nВыбери действие:",
        "uz": f"{E['gear']} <b>Admin panel</b>\n\nAmalni tanlang:",
        "en": f"{E['gear']} <b>Admin panel</b>\n\nChoose an action:",
    },
    "admin.no_access": {
        "ru": f"{E['lock']} У тебя нет доступа к админке.",
        "uz": f"{E['lock']} Sizda admin panelga kirish huquqi yo'q.",
        "en": f"{E['lock']} You don't have access to admin panel.",
    },
    "admin.stats": {
        "ru": (
            f"{E['chart']} <b>Статистика бота</b>\n\n"
            f"{E['users']} Всего юзеров: <b>{{total_users}}</b>\n"
            f"{E['star']} Новых юзеров сегодня: <b>{{today_users}}</b>\n"
            f"{E['download']} Всего скачиваний: <b>{{total_downloads}}</b>\n"
            f"{E['megaphone']} Каналов: <b>{{total_channels}}</b>"
        ),
        "uz": (
            f"{E['chart']} <b>Bot statistikasi</b>\n\n"
            f"{E['users']} Jami foydalanuvchilar: <b>{{total_users}}</b>\n"
            f"{E['star']} Bugungi yangi foydalanuvchilar: <b>{{today_users}}</b>\n"
            f"{E['download']} Jami yuklashlar: <b>{{total_downloads}}</b>\n"
            f"{E['megaphone']} Kanallar: <b>{{total_channels}}</b>"
        ),
        "en": (
            f"{E['chart']} <b>Bot statistics</b>\n\n"
            f"{E['users']} Total users: <b>{{total_users}}</b>\n"
            f"{E['star']} New users today: <b>{{today_users}}</b>\n"
            f"{E['download']} Total downloads: <b>{{total_downloads}}</b>\n"
            f"{E['megaphone']} Channels: <b>{{total_channels}}</b>"
        ),
    },
    "admin.channels_empty": {
        "ru": f"{E['megaphone']} <b>Каналы</b>\n\nСписок пуст. Добавь канал кнопкой ниже.",
        "uz": f"{E['megaphone']} <b>Kanallar</b>\n\nRo'yxat bo'sh. Quyidagi tugma orqali kanal qo'shing.",
        "en": f"{E['megaphone']} <b>Channels</b>\n\nList is empty. Add a channel using the button below.",
    },
    "admin.channels_title": {
        "ru": f"{E['megaphone']} <b>Каналы для подписки:</b>\n",
        "uz": f"{E['megaphone']} <b>Obuna kanallari:</b>\n",
        "en": f"{E['megaphone']} <b>Subscription channels:</b>\n",
    },
    "admin.add_channel_id": {
        "ru": (
            f"{E['megaphone']} <b>Добавление канала</b>\n\n"
            "Отправь <b>ID канала</b> (например <code>-1001234567890</code>)\n\n"
            f"{E['bulb']} Узнать ID: добавь бота @getmyid_bot в канал"
        ),
        "uz": (
            f"{E['megaphone']} <b>Kanal qo'shish</b>\n\n"
            "<b>Kanal ID</b> raqamini yuboring (masalan <code>-1001234567890</code>)\n\n"
            f"{E['bulb']} ID bilish: @getmyid_bot ni kanalga qo'shing"
        ),
        "en": (
            f"{E['megaphone']} <b>Add channel</b>\n\n"
            "Send the <b>channel ID</b> (e.g. <code>-1001234567890</code>)\n\n"
            f"{E['bulb']} Get ID: add @getmyid_bot to the channel"
        ),
    },
    "admin.add_channel_title": {
        "ru": f"{E['edit']} Теперь отправь <b>название канала</b>:",
        "uz": f"{E['edit']} Endi <b>kanal nomini</b> yuboring:",
        "en": f"{E['edit']} Now send the <b>channel name</b>:",
    },
    "admin.add_channel_link": {
        "ru": (
            f"{E['link']} Теперь отправь <b>ссылку или юзернейм канала</b>\n\n"
            "Принимаю любой формат:\n"
            "• <code>https://t.me/your_channel</code>\n"
            "• <code>@your_channel</code>\n"
            "• <code>your_channel</code>"
        ),
        "uz": (
            f"{E['link']} Endi <b>kanal havolasi yoki username</b> yuboring\n\n"
            "Istalgan formatda:\n"
            "• <code>https://t.me/your_channel</code>\n"
            "• <code>@your_channel</code>\n"
            "• <code>your_channel</code>"
        ),
        "en": (
            f"{E['link']} Now send the <b>channel link or username</b>\n\n"
            "Any format accepted:\n"
            "• <code>https://t.me/your_channel</code>\n"
            "• <code>@your_channel</code>\n"
            "• <code>your_channel</code>"
        ),
    },
    "admin.channel_added": {
        "ru": f"{E['check']} <b>Канал добавлен!</b>",
        "uz": f"{E['check']} <b>Kanal qo'shildi!</b>",
        "en": f"{E['check']} <b>Channel added!</b>",
    },
    "admin.confirm_delete": {
        "ru": f"{E['warning']} <b>Удалить канал?</b>\n\nID: <code>{{channel_id}}</code>\n\nЭто действие нельзя отменить.",
        "uz": f"{E['warning']} <b>Kanalni o'chirishni xohlaysizmi?</b>\n\nID: <code>{{channel_id}}</code>\n\nBu amalni qaytarib bo'lmaydi.",
        "en": f"{E['warning']} <b>Delete channel?</b>\n\nID: <code>{{channel_id}}</code>\n\nThis action cannot be undone.",
    },
    "admin.id_not_number": {
        "ru": f"{E['cross']} ID должен быть числом. Попробуй ещё раз:",
        "uz": f"{E['cross']} ID raqam bo'lishi kerak. Qayta urinib ko'ring:",
        "en": f"{E['cross']} ID must be a number. Try again:",
    },
    "admin.title_too_long": {
        "ru": f"{E['cross']} Название слишком длинное (макс 200 символов)",
        "uz": f"{E['cross']} Nom juda uzun (maks 200 belgi)",
        "en": f"{E['cross']} Name is too long (max 200 characters)",
    },
    "admin.link_invalid": {
        "ru": f"{E['cross']} Не удалось распознать ссылку.\nПопробуй ещё:",
        "uz": f"{E['cross']} Havolani aniqlab bo'lmadi.\nQayta urinib ko'ring:",
        "en": f"{E['cross']} Could not parse the link.\nTry again:",
    },
    "admin.no_access_alert": {
        "ru": f"{E['lock']} Нет доступа",
        "uz": f"{E['lock']} Kirish taqiqlangan",
        "en": f"{E['lock']} Access denied",
    },
    "admin.channel_deleted": {
        "ru": f"{E['check']} Канал удалён!",
        "uz": f"{E['check']} Kanal o'chirildi!",
        "en": f"{E['check']} Channel deleted!",
    },
    "admin.channel_not_found": {
        "ru": f"{E['cross']} Канал не найден",
        "uz": f"{E['cross']} Kanal topilmadi",
        "en": f"{E['cross']} Channel not found",
    },

    # === Кнопки админки ===
    "btn.admin_stats": {"ru": "Статистика", "uz": "Statistika", "en": "Statistics"},
    "btn.admin_channels": {"ru": "Каналы", "uz": "Kanallar", "en": "Channels"},
    "btn.admin_home": {"ru": "Главное меню", "uz": "Bosh menyu", "en": "Main menu"},
    "btn.admin_add": {"ru": "Добавить канал", "uz": "Kanal qo'shish", "en": "Add channel"},
    "btn.admin_back": {"ru": "Назад", "uz": "Orqaga", "en": "Back"},
    "btn.admin_cancel": {"ru": "Отмена", "uz": "Bekor qilish", "en": "Cancel"},
    "btn.admin_confirm_del": {"ru": "Да, удалить", "uz": "Ha, o'chirish", "en": "Yes, delete"},
    "btn.admin_cancel_del": {"ru": "Отмена", "uz": "Bekor qilish", "en": "Cancel"},
    "btn.admin_panel": {"ru": "Админ-панель", "uz": "Admin panel", "en": "Admin panel"},
    "btn.admin_broadcast": {"ru": "Рассылка", "uz": "Xabar yuborish", "en": "Broadcast"},

    # === Рассылка ===
    "admin.broadcast_prompt": {
        "ru": f"{E['plane']} <b>Массовая рассылка</b>\n\nОтправь текст/фото/видео для рассылки.\nПоддерживается HTML.",
        "uz": f"{E['plane']} <b>Ommaviy xabar</b>\n\nYuborish uchun matn/rasm/video yuboring.\nHTML qo'llab-quvvatlanadi.",
        "en": f"{E['plane']} <b>Mass broadcast</b>\n\nSend text/photo/video to broadcast.\nHTML supported.",
    },
    "admin.broadcast_preview": {
        "ru": f"{E['eye']} <b>Предпросмотр</b>\n\nОтправить это сообщение всем юзерам?",
        "uz": f"{E['eye']} <b>Oldindan ko'rish</b>\n\nBu xabarni barcha foydalanuvchilarga yuborishni xohlaysizmi?",
        "en": f"{E['eye']} <b>Preview</b>\n\nSend this message to all users?",
    },
    "admin.broadcast_confirm": {"ru": "Да, отправить", "uz": "Ha, yuborish", "en": "Yes, send"},
    "admin.broadcast_cancel": {"ru": "Отмена", "uz": "Bekor qilish", "en": "Cancel"},
    "admin.broadcast_started": {
        "ru": f"{E['plane']} Рассылка запущена... Ожидай отчёт.",
        "uz": f"{E['plane']} Xabar yuborilmoqda... Hisobotni kuting.",
        "en": f"{E['plane']} Broadcast started... Wait for report.",
    },
    "admin.broadcast_done": {
        "ru": f"{E['chart']} <b>Рассылка завершена!</b>\n\n{E['check']} Доставлено: <b>{{success}}</b>\n{E['cross']} Ошибок: <b>{{failed}}</b>\n{E['users']} Всего: <b>{{total}}</b>",
        "uz": f"{E['chart']} <b>Xabar yuborish tugadi!</b>\n\n{E['check']} Yetkazildi: <b>{{success}}</b>\n{E['cross']} Xatolar: <b>{{failed}}</b>\n{E['users']} Jami: <b>{{total}}</b>",
        "en": f"{E['chart']} <b>Broadcast complete!</b>\n\n{E['check']} Delivered: <b>{{success}}</b>\n{E['cross']} Failed: <b>{{failed}}</b>\n{E['users']} Total: <b>{{total}}</b>",
    },

    # === Рекламная подпись ===
    "download.promo": {
        "ru": f"\n\n{E['download']} Скачивай бесплатно через @{{bot_username}}",
        "uz": f"\n\n{E['download']} @{{bot_username}} orqali bepul yuklab oling",
        "en": f"\n\n{E['download']} Download for free via @{{bot_username}}",
    },

    # === Описания команд бота (для меню Telegram) ===
    "cmd.start": {
        "ru": "Запустить бота",
        "uz": "Botni boshlash",
        "en": "Start the bot",
    },
    "cmd.menu": {
        "ru": "Главное меню",
        "uz": "Asosiy menyu",
        "en": "Main menu",
    },
    "cmd.profile": {
        "ru": "Мой профиль",
        "uz": "Mening profilim",
        "en": "My profile",
    },
    "cmd.help": {
        "ru": "Помощь",
        "uz": "Yordam",
        "en": "Help",
    },
    "cmd.language": {
        "ru": "Сменить язык",
        "uz": "Tilni o'zgartirish",
        "en": "Change language",
    },
}


def t(key: str, lang: str = "ru", **kwargs) -> str:
    """Получить перевод по ключу и языку"""
    translations = TRANSLATIONS.get(key, {})
    text = translations.get(lang, translations.get("en", f"[{key}]"))
    if kwargs:
        text = text.format(**kwargs)
    return text


def detect_language(language_code: str | None) -> str:
    """Определяет язык по Telegram: ru → русский, uz → узбекский, остальное → английский"""
    if not language_code:
        return "ru"
    if language_code.startswith("ru"):
        return "ru"
    if language_code.startswith("uz"):
        return "uz"
    return "en"
