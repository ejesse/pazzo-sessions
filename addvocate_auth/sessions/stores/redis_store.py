from addvocate_auth.exceptions import SuspiciousOperation, \
    AddvocateAuthException
from addvocate_auth.sessions.base import CreateError
from addvocate_auth.utils import get_utc_now_with_timezone
import datetime
import redis
try:
    import cPickle as pickle
except ImportError:
    import pickle
    

class RedisStore(object):
    """ Handles redis connection pooling
    via singleton
    """
    __shared_state = dict(
        redis_session_pool=None,
        settings = {}
    )
    
    def __init__(self, settings=None):
        self.__dict__ = self.__shared_state
        if settings is not None:
            self.settings = settings
        
    def get_redis_session_connection(self):
        if not self.redis_session_pool:
            self.redis_session_pool = redis.ConnectionPool(max_connections=self.settings.REDIS_POOL_MAX_CONNECTIONS,host=self.settings.REDIS_SESSIONS_HOST, port=self.settings.REDIS_SESSIONS_PORT, db=self.settings.REDIS_SESSIONS_DB)
        return redis.Redis(connection_pool=self.redis_session_pool)

class RedisSessionEngine(object):
    """ The RedisSessionEngine handles operations
    for session persistence """
    
    def __init__(self,settings=None):
        self.settings = settings
        if self.settings is None:
            raise AddvocateAuthException("RedisSessionEngine requires settings")
        
    def load(self, session):
        """ Loads the data for the provided session 
        If the session has no data, is expired, or 
        the decode doesn't match hashes, then the
        session is re-created
        """
        r = RedisStore(settings=self.settings).get_redis_session_connection()
        raw = r.get(session.session_key)
        if raw is None:
            r.delete(session.session_key)
            session.create()
            return {}
        d = pickle.loads(raw)
        expire_date = d.get('expire_date',datetime.datetime(1980,1,1))
        if expire_date <  get_utc_now_with_timezone():
            session.create()
            return {}
        try:
            decoded = session.decode(d.get('session_data'))
            return decoded
        except SuspiciousOperation:
            session.create()
            return {}

    def exists(self, session_key):
        """ Checks to see if a session key already exists"""
        r = RedisStore(settings=self.settings).get_redis_session_connection()
        if r.get(session_key) is None:
            return False
        return True

    def create(self,session):
        """ Populates and persists a new empty session """
        session._session_key = session._get_new_session_key()
        session.modified = True
        session._session_cache = {}
        expiry = self.settings.SESSION_COOKIE_AGE
        expiry_date = get_utc_now_with_timezone() + datetime.timedelta(seconds=expiry)
        session.save(expiry_date=expiry_date)
        return

    def save(self, session, must_create=False, expiry_date=None):
        """
        Saves the current session data to redis. If 'must_create' is
        True, a database error will be raised if the saving operation doesn't
        create a *new* entry (as opposed to possibly updating an existing
        entry).
        """
        
        r = RedisStore(settings=self.settings).get_redis_session_connection()
        session_key = session._get_or_create_session_key()
        
        if must_create:
            test = r.get(session_key)
            if test is not None:
                raise CreateError()

        if expiry_date is None:
            expiry_date = session.get_expiry_date()
            
        session_dict = {'session_key':session_key,
                        'expire_date': expiry_date,
                        'session_data':session.encode(session._get_session(no_load=must_create))
            }
        session_json = pickle.dumps(session_dict)
        r.set(session_key,session_json)
        r.expire(session_key, session.get_expiry_age())
        

    def delete(self, session_key):
        """ Deletes the session with the associated session_key """
        r = RedisStore(settings=self.settings).get_redis_session_connection()
        r.delete(session_key)
        
class SessionEngine(RedisSessionEngine):
    pass
