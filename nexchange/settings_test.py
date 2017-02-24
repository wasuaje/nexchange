from .settings import *

# When testing, use sqlite3 so the database is loaded in memory
# this will make tests run faster
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
}

DEBUG = True
