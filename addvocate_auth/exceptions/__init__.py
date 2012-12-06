

class AddvocateAuthException(Exception):
    """Generic, picklable exception for Addvocate Auth"""
    def __init__(self, value):
        self.value = value
        self.message = value
    
    def __str__(self):
        return repr(self.value)
    
class SuspiciousOperation(AddvocateAuthException):
    "The user did something suspicious"
    pass