from django.conf import settings
from addvocate_auth.sessions.base import SessionBase
from importlib import import_module

class SessionStore(object):
    """
    Gets the addvocate session store from the settings and
    then impersonates a Django store
    """
    
    def __new__(self, *args, **kwargs):
        addvocate_session_store = import_module(settings.ADDVOCATE_SESSION_STORE)
        kwargs['settings'] = settings
        return addvocate_session_store.Session(self, settings=settings)
