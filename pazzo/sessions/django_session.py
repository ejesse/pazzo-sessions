from pazzo.sessions.base import BaseSession
from pazzo.sessions.stores.store_registry import StoreRegistry
from pazzo.exceptions import PazzoException

try:
    from django.conf import settings as django_settings
except ImportError:
    raise PazzoException("Django SessionStore requires Django")


class FauxSettings(object):
    pass


class SessionStore(BaseSession):

    """
    Gets the pazzo session store from the settings and
    then impersonates a Django store
    """

    def __init__(self, session_key=None):
        """ Sneakily set the settings from the Django settings
        so we can fool Django into initializing the registry
        and still behave like both a pazzo session
        and a Django SessionStore
        """
        registry = StoreRegistry()
        if not registry.initialized:
            settings = FauxSettings()
            ## silly django....
            settings.__dict__ = django_settings.__dict__['_wrapped'].__dict__
            StoreRegistry(settings=settings)
        super(SessionStore, self).__init__(session_key=session_key)
