from todo.settings_components.main_config import main_config

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': main_config.POSTGRES_DB,
        'USER': main_config.POSTGRES_USER,
        'PASSWORD': main_config.POSTGRES_PASSWORD,
        'HOST': main_config.POSTGRES_HOST,
        'PORT': main_config.POSTGRES_PORT,
        'OPTIONS': {
           'options': '-c search_path=public,diary'
        }
    }
}
