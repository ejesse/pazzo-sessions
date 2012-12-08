from Cookie import Cookie
from addvocate_auth.sessions.base import BaseSession
from addvocate_auth.sessions.stores.store_registry import StoreRegistry

def get_session_id_from_environ(environ, settings):

    session_key = environ.get(settings.SESSION_WSGI_ENVIRON_NAME)
    if session_key is not None:
        return session_key
    environ_cookie = Cookie()
    environ_cookie.load(environ.get('HTTP_COOKIE'))
    session_key = None
    if environ_cookie is not None:
        morsel = environ_cookie.get(settings.SESSION_COOKIE_NAME)
        if morsel is not None:
            session_key = morsel.value
    return session_key 
        

class WSGISession(BaseSession):
    pass

class Session(object):
    
    def __new__(self, environ):
        registry = StoreRegistry()
        settings = registry.settings
        session_key = get_session_id_from_environ(environ, settings)
        if session_key is not None:
            environ[settings.SESSION_WSGI_ENVIRON_NAME] = session_key
            session = BaseSession(session_key=session_key)
            return session
        return BaseSession()
    
#    def __init__(self, environ):
#        """ Adapts the base session to load from a WSGI
#        environ rather than a session_key. A bit
#        wonky since it requires passing in None
#        and THEN setting _session key :( 
#        """
#        BaseSession.__init__(self, session_key=None)
#        self._session_key = get_session_id_from_environ(environ, self.settings)
#        if self._session_key is not None:
#            environ[self.settings.SESSION_WSGI_ENVIRON_NAME] = self._session_key
#            registry = StoreRegistry()
#            if registry.sessions.has_key(self._session_key):
#                self = registry.sessions[self._session_key]
#            else:
#                self.load()
#                registry.sessions[self._session_key] = self
#        print self
#        print self.keys()