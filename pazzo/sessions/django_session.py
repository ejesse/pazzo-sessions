from pazzo.sessions.base import BaseSession
from importlib import import_module
from pazzo.sessions.stores.store_registry import StoreRegistry
from pazzo.exceptions import PazzoException

try:
    from django.conf import settings
except ImportError:
    raise PazzoException("Django SessionStore requires Django")


class SessionStore(BaseSession):
    
    """
    Gets the pazzo session store from the settings and
    then impersonates a Django store
    """
    
    def __init__(self, session_key=None):
        """ Sneakily set the settings from the Django settings
        so we can fool Django into initializing the registry
        and still behave like both an pazzo session
        and a Django SessionStore 
        """
        registry = StoreRegistry()
        if not registry.initialized:
            StoreRegistry(settings=settings)
        super(SessionStore, self ).__init__(session_key=session_key)