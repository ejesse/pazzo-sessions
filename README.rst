pazzo-sessions
=======================
Pazzo sessions provides generic, pseudo-synchronized, session storage for Python. The intent is to provide more reliable session storage for applications that have many, near-concurrent requests from the same user/session (think AJAX) and might include different frameworks running concurrently on the same domain (for example, both Django and Flask).

For most web applications, loading a session at the beginning of a request and saving it just before the response is sent to the client is sufficient. If this is all you need, then Pazzo is probably overkill and you should probably look at beaker or your framework's built-in session manaagement (such as Django's)

Pazzo is very "noisy" and should only be used with high-performance storage. Currently only redis is implemented, but memcache or other high-performance key/value stores could be used as well.

The Session interface itself borrows very heavily from Django's session implementation.

------------
Status
------------

Very alpha. Expect bugs. Currently only supports redis as a backend

------------
Installation
------------

Clone the repo. Install requirements, if necessary (e.g. ``pip install -r requirements.txt``). Run ``python setup.py install``

------------
Django configuration
------------

1. Add settings to your Django settings.py. These are in example_settings.py or::


	SESSION_COOKIE_AGE = 1209600 # Cookie age in seconds, 1209600 == two weeks 
	SESSION_EXPIRE_AT_BROWSER_CLOSE = False
	SESSION_COOKIE_NAME = 'sessionid'
	SESSION_COOKIE_DOMAIN = '127.0.0.1'
	SESSION_COOKIE_PATH = '/'
	SESSION_COOKIE_SECURE = None
	SESSION_COOKIE_HTTPONLY = None
	SESSION_WSGI_ENVIRON_NAME = 'pazzo_session'
	SESSION_KEY_SALT = "pazzo.sessions.base.BaseSession"
	PAZZO_SESSION_STORE = 'pazzo.sessions.stores.redis_store'
	REDIS_POOL_MAX_CONNECTIONS = 20
	REDIS_SESSIONS_HOST = 'localhost'
	REDIS_SESSIONS_PORT = 6379
	REDIS_SESSIONS_DB = 15
	SESSION_ENGINE = 'pazzo.sessions.django_session'
	SESSION_SECRET_KEY = 'secret'
		
You will need to have a SESSION_SECRET_KEY. This can be your Django SECRET_KEY or be separate. If you run multiple apps, they will all need to have the same SESSION_SECRET_KEY value. To generate a separate value::

	from pazzo.utils import get_secret_string
	print get_secret_string(64)

Copy that output to be the value of the SESSION_SECRET_KEY.

That should be it. You should now be able to use the sessions as if they were regular old Django sessions (note: you still have run have ``django.contrib.sessions.middleware.SessionMiddleware`` in your MIDDLEWARE_CLASSE ).

------------
WSGI configuration
------------

1. If you're using a WSGI micro framework like Flask or Bottle, the setup is slightly more complex than for Django. You will still need a settings module. This can be called settings.py or session_settings.py or whatever as long as it has the following attributes::

	SESSION_COOKIE_AGE = 1209600 # Cookie age in seconds, 1209600 == two weeks 
	SESSION_EXPIRE_AT_BROWSER_CLOSE = False
	SESSION_COOKIE_NAME = 'sessionid'
	SESSION_COOKIE_DOMAIN = '127.0.0.1'
	SESSION_COOKIE_PATH = '/'
	SESSION_COOKIE_SECURE = None
	SESSION_COOKIE_HTTPONLY = None
	SESSION_WSGI_ENVIRON_NAME = 'pazzo_session'
	SESSION_KEY_SALT = "pazzo.sessions.base.BaseSession"
	PAZZO_SESSION_STORE = 'pazzo.sessions.stores.redis_store'
	REDIS_POOL_MAX_CONNECTIONS = 20
	REDIS_SESSIONS_HOST = 'localhost'
	REDIS_SESSIONS_PORT = 6379
	REDIS_SESSIONS_DB = 15
	SESSION_SECRET_KEY = 'secret'
	
You will need to have a SESSION_SECRET_KEY. If you run multiple apps, they will all need to have the same SESSION_SECRET_KEY value. To generate a value::

	from pazzo.utils import get_secret_string
	print get_secret_string(64)

Copy that output to be the value of the SESSION_SECRET_KEY.

2. The session middleware will need to be configured. If you have an app object inside app.py, you can do::

	import settings
	from app import app
	from pazzo.sessions.middleware.wsgi_session_middleware import SessionMiddleware
	from pazzo.sessions.stores.store_registry import StoreRegistry

	if __name__ == '__main__':
    	registry = StoreRegistry(settings=settings)
    	app.wsgi_app = SessionMiddleware(app.wsgi_app)
    	app.run(debug=True)

3. To access the session, pass in the WSGI environ::

	from pazzo.sessions.wsgi_session import Session
	from flask import Flask, request, redirect
	
	app = Flask(__name__)
	
	@app.route('/')
	def hello_world():
	    start = time.time()
	    session = Session(request.environ)
	    session['foo'] = bar
	    ## do more stuff
	    return 'hello world'


4. That's it