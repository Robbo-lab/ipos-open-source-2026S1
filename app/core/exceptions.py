from pyexpat.errors import messages


class ValidationException(Exception):
    """Shared Valideation exception for core business logic. 
    
    Raise by core logic when input validatino fails. 
    Fast API routes are responsible for catching this and 
    converting it to an appropriate HTTP response.
    """

    def __init__(self, message: str = "Validation error"):
        self.message = messages
        super().__init__(message)