from todo.settings_components.main_config import REDIS_URL

CELERY_BROKER_URL: str = REDIS_URL+'/1'
CELERY_RESULT_BACKEND: str = REDIS_URL+'/1'

CELERY_TIMEZONE = 'Asia/Krasnoyarsk'
CELERY_CACHE_BACKEND = 'default'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
