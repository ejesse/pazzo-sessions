

class PazzoException(Exception):
    """Generic, picklable exception for Pazzo"""
    def __init__(self, value):
        self.value = value
        self.message = value

    def __str__(self):
        return repr(self.value)


class SuspiciousOperation(PazzoException):
    "The user did something suspicious"
    pass
