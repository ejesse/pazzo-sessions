pazzo-sessions
=======================
Pazzo sessions provides generic, pseudo-synchronized, session storage for Python. The intent is to provide more reliable session storage for applications that have many, near-concurrent requests from the same user/session (think AJAX) and might include different frameworks running concurrently on the same domain (for example, both Django and Flask).

For most web applications, loading a session at the beginning of a request and saving it just before the response is sent to the client is sufficient. If this is all you need, then Pazzo is probably overkill and you should look at beaker or your framework's built-in session management (such as Django's default session storage).

Pazzo is very "noisy" in terms of number of reads and writes and, as such, should only be used with high-performance storage. Currently only redis is implemented, but memcache or other high-performance key/value stores could be used as well.

The Session interface itself is inspired by, and borrows very heavily from, Django's session implementation.

------------
Usage notes
------------

With Pazzo, every time you access session data, you are hitting the persistence store, at least once. Every. Single. Time. This has serious load implications if you make heavy use of session data and is why Pazzo is only intended to be used by stores such as redis or memcache.

------------
Status
------------

Very alpha. Expect bugs. Currently only supports redis as a backend.

------------
Installation
------------

Clone the repo. Install requirements, if necessary (e.g. ``pip install -r requirements.txt``). Run ``python setup.py install``

------------
Django configuration
------------

1. Add the following to your Django settings.py. All possible settings are in example_settings.py but the two required Django settings are::

	SESSION_ENGINE = 'pazzo.sessions.django_session'
	SESSION_SECRET_KEY = 'secret'
		
Note that your SESSION_ENGINE might already be set! Replace its value with 'pazzo.sessions.django_session' to use Pazzo.
		
2. You will need to have a unique SESSION_SECRET_KEY. This can be set to your Django SECRET_KEY or be separate. If you run multiple apps, they will all need to have the same SESSION_SECRET_KEY value. To generate a separate value::

	from pazzo.utils import get_secret_string
	print get_secret_string(64)

Copy that output to be the value of the SESSION_SECRET_KEY.

The default settings will get most people up and running locally, other key settings include::

SESSION_COOKIE_DOMAIN = '127.0.0.1'
SESSION_COOKIE_PATH = '/'
REDIS_POOL_MAX_CONNECTIONS = 20
REDIS_SESSIONS_HOST = 'localhost'
REDIS_SESSIONS_PORT = 6379
REDIS_SESSIONS_DB = 15

3. Ensure that ``django.contrib.sessions.middleware.SessionMiddleware`` is in your MIDDLEWARE_CLASSES setting.

4. That should be it. You should now be able to use the sessions as if they were regular old Django sessions.

------------
WSGI configuration
------------

1. If you're using a WSGI micro framework like Flask or Bottle, the setup is slightly more complex than for Django. You will still need a settings module. This can be called settings.py or session_settings.py or whatever you like so long as it's passed in correctly in step 2. The only absolutely required setting is ``SESSION_SECRET_KEY`` If you run multiple apps, they will all need to have the same SESSION_SECRET_KEY value. To generate a value::

	from pazzo.utils import get_secret_string
	print get_secret_string(64)

Copy that output to be the value of the SESSION_SECRET_KEY. Additional optional settings (to set things such as redis host, cookie domain, etc) can be found in example_settings.py.

The default settings will get most people up and running locally, other key settings include::

SESSION_COOKIE_DOMAIN = '127.0.0.1'
SESSION_COOKIE_PATH = '/'
REDIS_POOL_MAX_CONNECTIONS = 20
REDIS_SESSIONS_HOST = 'localhost'
REDIS_SESSIONS_PORT = 6379
REDIS_SESSIONS_DB = 15

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