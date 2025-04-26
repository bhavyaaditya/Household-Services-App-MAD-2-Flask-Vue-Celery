import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY="secretkey"
    JWT_EXPIRATION_DELTA = timedelta(days=1)
    PASSWORD_RESET_EXPIRATION = timedelta(hours=1)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db') # "sqlite:///app.db"
    SECURITY_DEFAULT_REMEMBER_ME = False    # Required by function `login_user` in Flask-Security
    SECURITY_PASSWORD_HASH = 'argon2'
    SECURITY_PASSWORD_SALT = 'namak'

    CELERY_BROKER_URL = "redis://172.31.240.158:6379/0"
    CELERY_RESULT_BACKEND = "redis://172.31.240.158:6379/0"

    # broker_url = "redis://172.31.240.158:6379/0"
    # result_backend = "redis://172.31.240.158:6379/0"

    CACHE_TYPE = 'RedisCache'
    CACHE_REDIS_URL = 'redis://172.31.240.158:6379/3'
    DEFAULT_CACHE_TIMEOUT = 200
    REDIS_URL = 'redis://172.31.240.158:6379'

    SECURITY_UNAUTHORIZED_VIEW = None

    WTF_CSRF_ENABLED = False
    SECURITY_CSRF_PROTECT = False

    MAIL_SERVER = 'localhost'
    MAIL_PORT = 1025
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
    MAIL_USERNAME = ''
    MAIL_PASSWORD = ''
    MAIL_DEFAULT_SENDER = 'bhavya@aditya.com'
