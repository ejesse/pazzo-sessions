from django.conf import settings
from addvocate_auth.sessions.base import BaseSession
from importlib import import_module
from addvocate_auth.sessions.stores.store_registry import StoreRegistry

class SessionStore(BaseSession):
    
    """
    Gets the addvocate session store from the settings and
    then impersonates a Django store
    """
    
    def __init__(self, session_key=None):
        """ Sneakily set the settings from the Django settings
        so we can fool Django into initializing the registry
        and still behave like both an addvocate session
        and a Django SessionStore 
        """
        registry = StoreRegistry()
        if not registry.initialized:
            StoreRegistry(settings=settings)
        super(SessionStore, self ).__init__(session_key=session_key)