import yt_dlp
from loguru import logger
from pathlib import Path
from aiogram import Bot
from aiogram.types import Message, FSInputFile


def filename(opts: dict, audio_video: str) -> Path:
    try:
        with yt_dlp.YoutubeDL(opts) as yd:
            yd.download(audio_video)
        for i in Path().iterdir():
            if i.is_file():
                if audio_video[-11:] in str(i):
                    return i
    except Exception as error:
        logger.error(error)


async def download_video_audio(message: Message, bot: Bot) -> None:
    """ Скачивает аудио/видео с youtube """
    logger.info(f'{message.from_user.id}: {message.text}')
    user_id = message.chat.id
    try:
        audio_video_url = message.text.split(' ')
        ydl_opts = {}
        yt_link = ''
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(audio_video_url[0], download=False)
            extract = ydl.sanitize_info(info)
            channel = extract.get('channel', {})
            channel_follower_count = extract.get('channel_follower_count', {})
            channel_url = extract.get('channel_url', {})
            fulltitle = extract.get('fulltitle', {})
            upload_date = extract.get('upload_date', {})
            duration_string = extract.get('duration_string', {})
            view_count = extract.get('view_count', {})
            like_count = extract.get('like_count', {})
            comment_count = extract.get('comment_count', {})
            thumbnail = extract.get('thumbnail', {})
            fn = [i.get('url', {}) for i in extract.get('thumbnails', {})
                  if i.get('preference', {}) == -1]
            fg = str(fn)[2:-2]
            data = (f"\n<b>канал:</b>  {channel}\n<b>кол-во подписок на канал:"
                    f"</b>  {channel_follower_count}\n<b>url канала:</b> "
                    f" {channel_url}\n<b>название видео:</b>  {fulltitle}\n"
                    f"<b>дата загрузки:</b>  {upload_date}\n"
                    f"<b>длительность:</b>  {duration_string}\n"
                    f"<b>кол-во просмотров:</b>  {view_count}\n"
                    f"<b>кол-во лайков:</b>  {like_count}\n"
                    f"<b>кол-во комментариев:</b>  {comment_count}\n"
                    f"<b>превью max:</b>  {thumbnail}\n"
                    f"<b>превью jpg:</b>  {fg}\n")

            filetype = 'video'
            if len(audio_video_url) == 1:
                txt = (f'<b>Начинаю загрузку видео\nВнимание: если размер '
                       f'файла превышает 50МB, то телеграм его не пошлет</b>\n'
                       f'{data}')
                await bot.send_message(user_id, txt, parse_mode='HTML')

            elif len(audio_video_url) == 2 and audio_video_url[1] == 'audio':
                txt = f'<b>Начинаю загрузку аудио дорожки:</b> {data}'
                await bot.send_message(user_id, txt, parse_mode='HTML')
                ydl_opts = {'format': 'm4a/bestaudio/best'}
                filetype = 'audio'

            for formats in extract["formats"]:
                if formats.get('format_id') == '18':
                    yt_link = formats.get('url')
                if formats.get('format_id') == '22':
                    yt_link = formats.get('url')

            file = filename(ydl_opts, audio_video_url[0])
            caption = f'<b>Готово. Ваше {filetype}: {fulltitle}</b>'

            if filetype == 'video':
                await bot.send_video(user_id, FSInputFile(file),
                                     caption=caption, parse_mode='HTML')
            elif filetype == 'audio':
                await bot.send_audio(user_id, FSInputFile(file),
                                     caption=caption, parse_mode='HTML')
            # file.unlink()

    except Exception as error:
        text = '<b>Ограничение!!! Лимит на закачку ботом 50MB.</b>'
        await bot.send_message(user_id, text, parse_mode='HTML')
        if yt_link := f"<a href='{yt_link}'>прямая ссылка</a>":
            if user_id in (000000000,):
                await bot.send_message(user_id, yt_link, parse_mode='HTML')
        logger.error(error)
    finally:
        for i in Path().iterdir():
            if i.is_file():
                for e in ['.webm', '.mp4', '.m4a']:
                    if str(i).endswith(e):
                        i.unlink()
