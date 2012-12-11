from Cookie import Cookie
from addvocate_auth.sessions.base import BaseSession
from addvocate_auth.sessions.stores.store_registry import StoreRegistry

def get_session_id_from_environ(environ, settings):

    session = environ.get(settings.SESSION_WSGI_ENVIRON_NAME)
    if session is not None:
        if session.session_key is not None:
            return session.session_key
    
    session_key = None
    try:
        environ_cookie = Cookie()
        environ_cookie.load(environ.get('HTTP_COOKIE'))
        if environ_cookie is not None:
            morsel = environ_cookie.get(settings.SESSION_COOKIE_NAME)
            if morsel is not None:
                session_key = morsel.value
    except AttributeError:
        # cookie fail
        pass
    return session_key 
        

class WSGISession(BaseSession):
    pass

class Session(object):
    
    def __new__(self, environ):
        registry = StoreRegistry()
        settings = registry.settings
        if environ.has_key(settings.SESSION_WSGI_ENVIRON_NAME):
            return environ[settings.SESSION_WSGI_ENVIRON_NAME]
        else:
            session_key = get_session_id_from_environ(environ, settings)
            if session_key is not None:
                return BaseSession(session_key=session_key)
        return BaseSession()
    
#    def __init__(self, environ):
#        """ Adapts the base session to load from a WSGI
#        environ rather than a session_key. A bit
#        wonky :( 
#        """
#        registry = StoreRegistry()
#        settings = registry.settings
#        if environ.has_key(settings.SESSION_WSGI_ENVIRON_NAME):
#            print "found session in environment"
#            self = environ[settings.SESSION_WSGI_ENVIRON_NAME]
#        else:
#            session_key = get_session_id_from_environ(environ, settings)
#            if session_key is not None:
#                print "found session_key %s" % session_key
#            BaseSession.__init__(self, session_key=session_key)
        