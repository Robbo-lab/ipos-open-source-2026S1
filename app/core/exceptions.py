class ValidationError(Exception):
    """Shared Validation exception for core business logic. 
    
    Raised by core logic when input validation fails. 
    Fast API routes are responsible for catching this and 
    converting it to an appropriate HTTP response.
    """

    def __init__(self, message: str = "Validation error"):
        self.message = message
        super().__init__(message)