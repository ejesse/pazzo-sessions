from Cookie import Cookie
from pazzo.sessions.base import BaseSession
from pazzo.sessions.stores.store_registry import StoreRegistry


def get_session_id_from_environ(environ, settings):
    """ Examines provided WSGI environ and settings
    and extracts the session ID either from the environ
    or from a cookie.

    Returns None if no session ID is found
    """
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


class Session(object):
    """ The session object wants to be instantiated
    via a session_key (because of the class' Django
    roots), but with WSGI it's a cleaner pattern
    to extract it from the WSGI environ, so we provide
    the Session class to return a BaseSession instance
    via a provided environ
    """

    def __new__(self, environ):
        registry = StoreRegistry()
        settings = registry.settings
        if settings.SESSION_WSGI_ENVIRON_NAME in environ:
            return environ[settings.SESSION_WSGI_ENVIRON_NAME]
        else:
            session_key = get_session_id_from_environ(environ, settings)
            if session_key is not None:
                return BaseSession(session_key=session_key)
        return BaseSession()
