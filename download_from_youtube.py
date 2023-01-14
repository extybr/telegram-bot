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
            stream.get_highest_resolution().download('youtube', f'{yt.title}.mp4')
            with open(f'youtube/{yt.title}.mp4', 'rb') as video:
                await bot.send_video(user_id, video, caption=f'*Готово. Ваше видео*: *{yt.title}*',
                                     parse_mode='Markdown')
                os.remove(f'youtube/{yt.title}.mp4')
        elif len(audio_video_url) == 2 and audio_video_url[1] == 'audio':
            yt = YouTube(audio_video_url[0])
            await bot.send_message(message.chat.id, f'*Начинаю загрузку аудио дорожки*: *{yt.title}'
                                                    f'*\n*С канала*: [{yt.author}]({yt.channel_url})',
                                   parse_mode='Markdown')
            stream = yt.streams.filter(only_audio=True).first()
            stream.download('youtube', f'{yt.title}.mp4')
            os.rename(f'youtube/{yt.title}.mp4', f'youtube/{yt.title}.mp3')
            with open(f'youtube/{yt.title}.mp3', 'rb') as audio:
                await bot.send_audio(user_id, audio, caption=f'*Готово. Ваше аудио*: *{yt.title}*',
                                     parse_mode='Markdown')
                os.remove(f'youtube/{yt.title}.mp3')
        else:
            await bot.send_message(message.chat.id, 'Некорректная ссылка!!!')
    except NetworkError as error:
        await bot.send_message(message.chat.id, '*Ограничение!!! Лимит на закачку ботом 50MB*.',
                               parse_mode='Markdown')
        if os.path.exists(f'youtube/{yt.title}.mp4'):
            os.remove(f'youtube/{yt.title}.mp4')
        elif os.path.exists(f'youtube/{yt.title}.mp3'):
            os.remove(f'youtube/{yt.title}.mp3')
        logger.error(error)
