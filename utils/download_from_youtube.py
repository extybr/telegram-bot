import yt_dlp
from loguru import logger
from pathlib import Path
from aiogram import Bot
from aiogram.types import Message, FSInputFile


async def download_video_audio(message: Message, bot: Bot) -> None:
    """ Скачивает аудио/видео с youtube """
    logger.info(f'{message.chat.id}: {message.text}')
    user_id = message.from_user.id
    try:
        audio_video_url = message.text.split(' ')
        ydl_opts = {}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(audio_video_url[0], download=False)
            extract = ydl.sanitize_info(info)
            channel = extract['channel']
            channel_follower_count = extract['channel_follower_count']
            channel_url = extract['channel_url']
            fulltitle = extract['fulltitle']
            upload_date = extract['upload_date']
            duration_string = extract['duration_string']
            view_count = extract['view_count']
            like_count = extract['like_count']
            comment_count = extract['comment_count']
            thumbnail = extract['thumbnail']
            fn = [i['url'] for i in extract['thumbnails'] if i['preference'] == -1]
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
            if len(audio_video_url) == 1:
                txt = (f'<b>Начинаю загрузку видео\nВнимание: если размер '
                       f'файла превышает 50МB, то телеграм его не пошлет</b>\n'
                       f'{data}')
                await bot.send_message(message.chat.id, txt, parse_mode='HTML')
                title = extract['fulltitle']
                with yt_dlp.YoutubeDL() as yd:
                    yd.download(audio_video_url[0])
                for i in Path().iterdir():
                    if str(i).startswith(title):
                        ext = str(i)[-4:] if str(i)[-4] == '.' else str(i)[-5:]
                        file = i.rename(title + ext)
                        video = FSInputFile(file)
                        caption = f'<b>Готово. Ваше видео: {title}</b>'
                        await bot.send_video(user_id, video, caption=caption,
                                             parse_mode='HTML')
                        file.unlink()
            elif len(audio_video_url) == 2 and audio_video_url[1] == 'audio':
                txt = f'Начинаю загрузку аудио дорожки: {data}'
                await bot.send_message(message.chat.id, txt, parse_mode='HTML')
                ydl_opts = {
                    'format': 'm4a/bestaudio/best'}
                with yt_dlp.YoutubeDL(ydl_opts) as yd:
                    yd.download(audio_video_url[0])
                title = extract['fulltitle']
                for i in Path().iterdir():
                    if str(i).startswith(title):
                        ext = str(i)[-4:] if str(i)[-4] == '.' else str(i)[-5:]
                        file = i.rename(title + ext)
                        audio = FSInputFile(file)
                        caption = f'<b>Готово. Ваше аудио: {title}</b>'
                        await bot.send_audio(user_id, audio, caption=caption,
                                             parse_mode='HTML')
                        file.unlink()
            else:
                await bot.send_message(message.chat.id, 'Некорректная ссылка!!!')
    except Exception as error:
        text = '<b>Ограничение!!! Лимит на закачку ботом 50MB.</b>'
        await bot.send_message(message.chat.id, text, parse_mode='HTML')
        for i in Path().iterdir():
            if str(i).startswith(fulltitle):
                i.unlink()
        logger.error(error)
