from dataclasses import dataclass
from environs import Env


@dataclass
class TgBot:
    token: str
    admin_ids: list[int]
    user_ids: list[int]
    flag: dict


@dataclass
class Config:
    tg_bot: TgBot


def load_config(path: str or None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(tg_bot=TgBot(
                    token=env('TOKEN'),
                    admin_ids=list(map(int, env.list('ADMIN_IDS'))),
                    user_ids=list(map(int, env.list('USER_IDS'))),
                    flag=dict()))
