from datetime import timedelta

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 5,

    'DATE_INPUT_FORMATS': ['%d.%m.%Y'],
    'DATETIME_INPUT_FORMATS': ['%d.%m.%Y %H:%M:%S'],
    'TIME_INPUT_FORMATS': '%H:%M:%S',

    'TIME_FORMAT': '%H:%M:%S',
    'DATETIME_FORMAT': '%d.%m.%Y %H:%M:%S',
    'DATE_FORMAT': '%d.%m.%Y',

    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],

    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],

    'DEFAULT_THROTTLE_CLASSES': [
        'todo.custom_throttling_params.FloodRateThrottle',
        'todo.custom_throttling_params.BurstRateThrottle',
        'todo.custom_throttling_params.SustainedRateThrottle',
        'todo.custom_throttling_params.NormalRateThrottle',
    ],

    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',

    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),

    'DEFAULT_THROTTLE_RATES': {
        'flood': '3/sec',
        'burst': '60/min',
        'normal': '1000/hour',
        'sustained': '5000/day'
    },
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Diary API',
    'VERSION': '1.0.0'
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}
