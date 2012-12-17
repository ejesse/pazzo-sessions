from pazzo.exceptions import PazzoException
from importlib import import_module
from pazzo.sessions.stores import default_settings


class StoreRegistry(object):
    """
    Singleton that handles settings
    """

    __shared_state = dict(
        session_engine=None,
        settings=None,
        initialized=False,
        sessions={}
    )

    def __init__(self, settings=None):
        self.__dict__ = self.__shared_state
        if self.session_engine is None:
            if settings is not None:
                self.settings = default_settings
                ## override the defaults
                for k in settings.__dict__.keys():
                    self.settings.__dict__[k] = settings.__dict__[k]
            if self.settings is not None:
                session_module = import_module(
                                    self.settings.PAZZO_SESSION_STORE)
                self.session_engine = session_module.SessionEngine(
                                                    settings=self.settings)
        if self.session_engine is not None and self.settings is not None:
            self.initialized = True

    def get_session_store(self):
        if not self.initialized:
            raise PazzoException("Session registry is not initialized. "
                        + "Call with StoreRegistry(settings=settings)")
        return self.session_engine
