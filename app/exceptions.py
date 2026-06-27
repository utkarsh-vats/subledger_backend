from fastapi import status

class SubLedgerError(Exception):
    """Base for all domain exceptions."""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, message=None, details=None):
        self.message = message or self.__class__.__doc__ or self.__class__.__name__
        self.details = details
        super().__init__(self.message)

    def to_dict(self):
        error = {"message": self.message}
        if self.details is not None:
            error["details"] = self.details
        return error

    def __str__(self):
        return self.message

class NotFoundError(SubLedgerError):    # 404   
    """Raised when a resource doesn't exist."""
    status_code = status.HTTP_404_NOT_FOUND

# ValidationError → 400 Bad Request
# We use 400 (not 422) for domain rule violations like illegal state
# transitions. 422 is reserved for FastAPI/Pydantic input parsing failures
# (malformed JSON, type mismatches, etc). This keeps the contract clean:
# 422 = "your request didn't parse"; 400 = "your request parsed but
# violates business rules."
class ValidationError(SubLedgerError):  # 400
    """Raised when a business rule is violated."""
    status_code = status.HTTP_400_BAD_REQUEST

class ConflictError(SubLedgerError):    # 409
    """Raised when a state conflict prevents an action."""
    status_code = status.HTTP_409_CONFLICT