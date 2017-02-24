from .settings_dev import *
import dj_database_url


DEBUG = True

ALLOWED_HOSTS += ['staging.nexchange.ru', ]

DATABASES = {
    'default': dj_database_url.config(default='postgis://{}:{}@{}:{}/{}'
                                      .format(user, password, host, port, db))

}
