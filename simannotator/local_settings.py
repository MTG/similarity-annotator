
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',
        'USER': 'postgres',
        'HOST': 'db',
        'PORT': '5432',
    }
}

MEDIA_ROOT = "/code/simannotator/media"
TEMP_ROOT = "/code/simannotator/tmp"

GEARMAN_JOB_SERVERS = ["localhost:4730"]

