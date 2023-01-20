from aiogram.utils.exceptions import NetworkError
from aiogram import types
from loguru import logger
from pytube import YouTube
import os.path


async def download_video_audio(message: types.Message, bot) -> None:
    """ Скачивает аудио/видео с youtube """
    logger.info(f'{message.chat.id}: {message.text}')
    user_id = message.from_user.id
    audio_video_url = message.text.split(' ')
    yt = YouTube(message.text)
    try:
        if len(audio_video_url) == 1:
            await bot.send_message(message.chat.id, f'*Начинаю загрузку видео*: *{yt.title}*\n'
                                                    f'*С канала*: [{yt.author}]({yt.channel_url})',
                                   parse_mode='Markdown')
            stream = yt.streams.filter(progressive=True, file_extension='mp4')
            title = f'{yt.title}'.replace('\\', '_').replace('/', '_').replace('|', '_')
            stream.get_highest_resolution().download('youtube', f'{title}.mp4')
            video = types.InputFile(os.path.join('youtube', f'{title}.mp4'))
            caption = f'*Готово. Ваше видео*: *{yt.title}*'
            await bot.send_video(user_id, video, caption=caption, parse_mode='Markdown')
            os.remove(os.path.join('youtube', f'{title}.mp4'))
        elif len(audio_video_url) == 2 and audio_video_url[1] == 'audio':
            yt = YouTube(audio_video_url[0])
            await bot.send_message(message.chat.id, f'*Начинаю загрузку аудио дорожки*: *{yt.title}'
                                                    f'*\n*С канала*: [{yt.author}]({yt.channel_url})',
                                   parse_mode='Markdown')
            stream = yt.streams.filter(only_audio=True).first()
            title = f'{yt.title}'.replace('\\', '_').replace('/', '_').replace('|', '_')
            stream.download('youtube', f'{title}.mp3')
            audio = types.InputFile(os.path.join('youtube', f'{title}.mp3'))
            caption = f'*Готово. Ваше аудио*: *{yt.title}*'
            await bot.send_audio(user_id, audio, caption=caption, parse_mode='Markdown')
            os.remove(os.path.join('youtube', f'{title}.mp3'))
        else:
            await bot.send_message(message.chat.id, 'Некорректная ссылка!!!')
    except NetworkError as error:
        await bot.send_message(message.chat.id, '*Ограничение!!! Лимит на закачку ботом 50MB*.',
                               parse_mode='Markdown')
        for file in os.listdir('youtube'):
            if file.endswith('.mp4') or file.endswith('.mp3'):
                os.remove(os.path.join('youtube', file))
        logger.error(error)
