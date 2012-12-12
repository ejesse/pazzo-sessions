from Cookie import Cookie
from addvocate_auth.exceptions import AddvocateAuthException
from addvocate_auth.sessions.stores.store_registry import StoreRegistry
from addvocate_auth.sessions.wsgi_session import Session
from werkzeug.http import cookie_date
import time

def me_want_cookie(key, value='', max_age=None, expires=None, path='/',
                   domain=None, secure=False, httponly=False):
        """
        Sets a cookie.

        ``expires`` can be:
        - a string in the correct format

        """
        
        cookie= Cookie()
        cookie[key] = value
        
        if expires is not None:
            cookie[key]['expires'] = expires
        if max_age is not None:
            cookie[key]['max-age'] = max_age
            # IE requires expires, so set it if hasn't been already.
            if not expires:
                cookie[key]['expires'] = cookie_date(time.time() +
                                                           max_age)
        if path is not None:
            cookie[key]['path'] = path
        if domain is not None:
            cookie[key]['domain'] = domain
        if secure:
            cookie[key]['secure'] = True
        if httponly:
            cookie[key]['httponly'] = True
            
        return cookie


class SessionMiddleware(object):
    
    def __init__(self, app):
        store_registry = StoreRegistry()
        if not store_registry.initialized:
            raise AddvocateAuthException("Session store registry not initialized")
        self.settings = store_registry.settings
        self.app = app
        self.registry = store_registry
        
    def __call__(self, environ, start_response):
        # just make sure it exists and throw it in the environ
        session = Session(environ)
        if session.session_key is None:
            session.create()
        environ[self.settings.SESSION_WSGI_ENVIRON_NAME] = session
        
        def session_start_response(status, headers, exc_info=None):
            session = Session(environ)
            if session.modified:
                if session.get_expire_at_browser_close():
                    max_age = None
                    expires = None
                else:
                    max_age = session.get_expiry_age()
                    expires_time = time.time() + max_age
                    expires = cookie_date(expires_time)
                cookie = me_want_cookie('sessionid', 
                                        value = session.session_key, 
                                        max_age = max_age, expires = expires, 
                                        path = self.settings.SESSION_COOKIE_PATH, 
                                        domain = self.settings.SESSION_COOKIE_DOMAIN, 
                                        secure = self.settings.SESSION_COOKIE_SECURE, 
                                        httponly = self.settings.SESSION_COOKIE_HTTPONLY)
                headers.append(("Set-Cookie",cookie.output(header='')))
            return start_response(status, headers, exc_info)
        
        return self.app(environ, session_start_response)
    