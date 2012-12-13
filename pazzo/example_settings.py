""" General cookie settings """

SESSION_COOKIE_AGE = 1209600 # Cookie age in seconds, 1209600 == two weeks 
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_NAME = 'sessionid'
SESSION_COOKIE_DOMAIN = '127.0.0.1'
SESSION_COOKIE_PATH = '/'
SESSION_COOKIE_SECURE = None
SESSION_COOKIE_HTTPONLY = None
SESSION_WSGI_ENVIRON_NAME = 'pazzo_session'
SESSION_KEY_SALT = "pazzo.sessions.base.BaseSession"

"""
Generate a secret key (You can use different number than 64):

from pazzo.utils import get_secret_string
print get_secret_string(64)

Copy that output to be the value of the SESSION_SECRET_KEY

"""
SESSION_SECRET_KEY = 'secret'

""" Persistence settings"""
PAZZO_SESSION_STORE = 'pazzo.sessions.stores.redis_store'
REDIS_POOL_MAX_CONNECTIONS = 20
REDIS_SESSIONS_HOST = 'localhost'
REDIS_SESSIONS_PORT = 6379
REDIS_SESSIONS_DB = 15
REDIS_SESSIONS_PASSWORD = None

""" Required for Django only """
SESSION_ENGINE = 'pazzo.sessions.django_session'
