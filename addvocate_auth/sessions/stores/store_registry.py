from addvocate_auth.exceptions import AddvocateAuthException
from importlib import import_module



class StoreRegistry(object):
    
    __shared_state = dict(
        session_engine=None,
        settings = None,
        initialized=False
    )
    
    def __init__(self, settings=None):
        self.__dict__ = self.__shared_state
        if self.session_engine is None:
            if settings is not None:
                self.settings = settings
            if self.settings is not None:
                session_module = import_module(settings.ADDVOCATE_SESSION_STORE)
                self.session_engine = session_module.SessionEngine(settings=self.settings)
        if self.session_engine is not None and self.settings is not None:
            self.initialized=True
            
    def get_session_store(self):
        if not self.initialized:
            raise AddvocateAuthException("Session registry is not initialized. Call with StoreRegistry(settings=settings)")
        return self.session_engine