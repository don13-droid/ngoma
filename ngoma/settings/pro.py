from .base import *
DEBUG = True

ADMINS = (
        ('Donewell', 'donewell@brandsbydart.com'),
        )
ALLOWED_HOSTS = ['ngoma.co.zw', 'www.ngoma.co.zw','127.0.0.1', 'ngoma-lwo3.onrender.com']
DATABASES = {
        'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ngoma',
        'USER': 'ngoma',
        'PASSWORD': 'cheatcode',

    }
}
