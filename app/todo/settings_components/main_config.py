from pydantic import BaseSettings, Field


class Config(BaseSettings):
    DEBUG: bool = Field(env='DEBUG')
    SECRET_KEY: str = Field(env='SECRET_KEY')
    REDIS_PASSWORD: str = Field(env='REDIS_PASSWORD')
    REDIS_HOST: str = Field(env='REDIS_HOST')
    REDIS_USER: str = Field(env='REDIS_USER', default='')
    REDIS_PORT: str = Field(env='REDIS_PORT')

    POSTGRES_DB: str = Field(env='POSTGRES_DB')
    POSTGRES_USER: str = Field(env='POSTGRES_USER')
    POSTGRES_PASSWORD: str = Field(env='POSTGRES_PASSWORD')
    POSTGRES_HOST: str = Field(env='POSTGRES_HOST')
    POSTGRES_PORT: str = Field(env='POSTGRES_PORT')

    DIARY_DAYS_EXPIRATION: int = Field(env='DIARY_DAYS_EXPIRATION', default=3)

    class Config:
        env_file = '../.dev.env'
        env_file_encoding = 'utf-8'


main_config: Config = Config()

REDIS_URL = (f'redis://{main_config.REDIS_USER}:'
             f'{main_config.REDIS_PASSWORD}@'
             f'{main_config.REDIS_HOST}:'
             f'{main_config.REDIS_PORT}')
