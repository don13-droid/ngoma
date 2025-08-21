from .base import *
DEBUG = True

ADMINS = (
        ('Donewell', 'donewell@brandsbydart.com'),
        )
ALLOWED_HOSTS = ['ngoma.co.zw', 'www.ngoma.co.zw','127.0.0.1', .'ngoma-3sq0.onrender.com']
DATABASES = {
        'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
    }
