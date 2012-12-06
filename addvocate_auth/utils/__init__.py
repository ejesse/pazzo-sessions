import hashlib
import hmac
import datetime
import pytz


def constant_time_compare(val1, val2):
    """
    Returns True if the two strings are equal, False otherwise.

    The time taken is independent of the number of characters that match.
    """
    if len(val1) != len(val2):
        return False
    result = 0
    for x, y in zip(val1, val2):
        result |= ord(x) ^ ord(y)
    return result == 0

def salted_hmac(key_salt, value, secret=None):
    """
    Returns the HMAC-SHA1 of 'value', using a key generated from key_salt and a
    secret.

    A different key_salt should be passed in for every application of HMAC.
    """
    if secret is None:
        raise AttributeError("salted_hmac requires a secret= value")

    # We need to generate a derived key from our base key.  We can do this by
    # passing the key_salt and our base key through a pseudo-random function and
    # SHA1 works nicely.
    key = hashlib.sha1((key_salt + secret).encode('utf-8')).digest()

    # If len(key_salt + secret) > sha_constructor().block_size, the above
    # line is redundant and could be replaced by key = key_salt + secret, since
    # the hmac module does the same thing for keys longer than the block size.
    # However, we need to ensure that we *always* do this.
    return hmac.new(key, msg=value, digestmod=hashlib.sha1)

def get_utc_now_with_timezone():
    """ Convenience method. Returns a "now" 
    utc datetime instance with a UTC timezone set 
    """
    d = datetime.datetime.utcnow()
    tz = pytz.timezone('utc')
    d = d.replace(tzinfo=tz)
    return d

def json_date_serializer(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj