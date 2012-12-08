import base64
import time
import base64

import OpenSSL
from datetime import datetime, timedelta
from addvocate_auth.utils import constant_time_compare, salted_hmac, get_utc_now_with_timezone
from addvocate_auth.exceptions import SuspiciousOperation, AddvocateAuthException
from addvocate_auth.sessions.stores.store_registry import StoreRegistry
try:
    import cPickle as pickle
except ImportError:
    import pickle

class CreateError(Exception):
    """
    Used internally as a consistent exception type to catch from save (see the
    docstring for SessionBase.save() for details).
    """
    pass

class SimpleSession(object):
    
    def __init__(self):
        self.session_key = None
        self.session_data = None
        self.expire_date = None

class BaseSession(object):
    """
    Base class for all Session classes.
    """
    TEST_COOKIE_NAME = 'testcookie'
    TEST_COOKIE_VALUE = 'worked'

    def __init__(self, session_key=None):
        self._session_key = session_key
        self.accessed = False
        self.modified = False
        registry = StoreRegistry()
        if registry.initialized:
            self.settings = registry.settings
            self.session_engine = registry.get_session_store()
        else:
            raise AddvocateAuthException("Session StoreRegistry is uninitialized")
        self._get_session()

    def __contains__(self, key):
        return key in self._session

    def __getitem__(self, key):
        return self._session[key]

    def __setitem__(self, key, value):
        self._session[key] = value
        self.modified = True

    def __delitem__(self, key):
        del self._session[key]
        self.modified = True

    def get(self, key, default=None):
        return self._session.get(key, default)

    def pop(self, key, *args):
        self.modified = self.modified or key in self._session
        return self._session.pop(key, *args)

    def setdefault(self, key, value):
        if key in self._session:
            return self._session[key]
        else:
            self.modified = True
            self._session[key] = value
            return value

    def set_test_cookie(self):
        self[self.TEST_COOKIE_NAME] = self.TEST_COOKIE_VALUE

    def test_cookie_worked(self):
        return self.get(self.TEST_COOKIE_NAME) == self.TEST_COOKIE_VALUE

    def delete_test_cookie(self):
        del self[self.TEST_COOKIE_NAME]

    def _hash(self, value):
        key_salt = "addvocate_auth.sessions." + self.__class__.__name__
        return salted_hmac(key_salt, value, self.settings.SECRET_SESSION_KEY).hexdigest()

    def encode(self, session_dict):
        "Returns the given session dictionary pickled and encoded as a string."
        pickled = pickle.dumps(session_dict)
        hash = self._hash(pickled)
        return base64.encodestring(hash + ":" + pickled)

    def decode(self, session_data):
        encoded_data = base64.decodestring(session_data)
        try:
            # could produce ValueError if there is no ':'
            hash, pickled = encoded_data.split(':', 1)
            expected_hash = self._hash(pickled)
            if not constant_time_compare(hash, expected_hash):
                raise SuspiciousOperation("Session data corrupted")
            else:
                return pickle.loads(pickled)
        except Exception:
            # ValueError, SuspiciousOperation, unpickling exceptions. If any of
            # these happen, just return an empty dictionary (an empty session).
            return {}

    def update(self, dict_):
        self._session.update(dict_)
        self.modified = True

    def has_key(self, key):
        return key in self._session

    def keys(self):
        return self._session.keys()

    def values(self):
        return self._session.values()

    def items(self):
        return self._session.items()

    def iterkeys(self):
        return self._session.iterkeys()

    def itervalues(self):
        return self._session.itervalues()

    def iteritems(self):
        return self._session.iteritems()

    def clear(self):
        # To avoid unnecessary persistent storage accesses, we set up the
        # internals directly (loading data wastes time, since we are going to
        # set it to an empty dict anyway).
        self._session_cache = {}
        self.accessed = True
        self.modified = True

    def _get_new_session_key(self):
        "Returns session key that isn't being used."
        return base64.b64encode(OpenSSL.rand.bytes(64))

    def _get_or_create_session_key(self):
        if self._session_key is None:
            self._session_key = self._get_new_session_key()
        return self._session_key

    def _get_session_key(self):
        return self._session_key

    session_key = property(_get_session_key)

    def _get_session(self, no_load=False):
        """
        Lazily loads session from storage (unless "no_load" is True, when only
        an empty dict is stored) and stores it in the current instance.
        """
        self.accessed = True
        try:
            return self._session_cache
        except AttributeError:
            if self.session_key is None or no_load:
                self._session_cache = {}
            else:
                self._session_cache = self.load()
        return self._session_cache

    _session = property(_get_session)

    def get_expiry_age(self):
        """Get the number of seconds until the session expires."""
        expiry = self.get('_session_expiry')
        if not expiry:   # Checks both None and 0 cases
            return self.settings.SESSION_COOKIE_AGE
        if not isinstance(expiry, datetime):
            return expiry
        delta = expiry - get_utc_now_with_timezone()
        return delta.days * 86400 + delta.seconds

    def get_expiry_date(self):
        """Get session the expiry date (as a datetime object)."""
        expiry = self.get('_session_expiry')
        if isinstance(expiry, datetime):
            return expiry
        if not expiry:   # Checks both None and 0 cases
            expiry = self.settings.SESSION_COOKIE_AGE
        return get_utc_now_with_timezone() + timedelta(seconds=expiry)

    def set_expiry(self, value):
        """
        Sets a custom expiration for the session. ``value`` can be an integer,
        a Python ``datetime`` or ``timedelta`` object or ``None``.

        If ``value`` is an integer, the session will expire after that many
        seconds of inactivity. If set to ``0`` then the session will expire on
        browser close.

        If ``value`` is a ``datetime`` or ``timedelta`` object, the session
        will expire at that specific future time.

        If ``value`` is ``None``, the session uses the global session expiry
        policy.
        """
        if value is None:
            # Remove any custom expiration for this session.
            try:
                del self['_session_expiry']
            except KeyError:
                pass
            return
        if isinstance(value, timedelta):
            value = get_utc_now_with_timezone() + value
        self['_session_expiry'] = value

    def get_expire_at_browser_close(self):
        """
        Returns ``True`` if the session is set to expire when the browser
        closes, and ``False`` if there's an expiry date. Use
        ``get_expiry_date()`` or ``get_expiry_age()`` to find the actual expiry
        date/age, if there is one.
        """
        if self.get('_session_expiry') is None:
            return self.settings.SESSION_EXPIRE_AT_BROWSER_CLOSE
        return self.get('_session_expiry') == 0

    def flush(self):
        """
        Removes the current session data from the database and regenerates the
        key.
        """
        self.clear()
        self.delete()
        self.create()

    def cycle_key(self):
        """
        Creates a new session key, whilst retaining the current session data.
        """
        data = self._session_cache
        key = self.session_key
        self.create()
        self._session_cache = data
        self.delete(key)

    # Methods that child classes must implement.

    def exists(self, session_key):
        """
        Returns True if the given session_key already exists.
        """
        return self.session_engine.exists(session_key)

    def create(self):
        """
        Creates a new session instance. Guaranteed to create a new object with
        a unique key and will have saved the result once (with empty data)
        before the method returns.
        """
        return self.session_engine.create(self)

    def save(self, must_create=False):
        """
        Saves the session data. If 'must_create' is True, a new session object
        is created (otherwise a CreateError exception is raised). Otherwise,
        save() can update an existing object with the same key.
        """
        self.session_engine.save(self, must_create)
        registry = StoreRegistry()
        registry.sessions[self.session_key] = self

    def delete(self, session_key=None):
        """
        Deletes the session data under this key. If the key is None, the
        current session key value is used.
        """
        if session_key is None:
            if self.session_key is None:
                return
            session_key = self.session_key

        self.session_engine.delete(session_key)

    def load(self):
        """
        Loads the session data and returns a dictionary.
        """
        return self.session_engine.load(self)
