
__all__ = [
    "APIException",
    "generate_exception",
    "ClientError",
    "ServerError",
    "InputError",
    "BadRequest",
    "Forbidden",
    "NotFound",
    "TooManyRequests",
    "InternalError",
    "Maintenance",
    "InvalidTag",
]

class APIException(Exception):
    """Base class for all API exceptions"""
    def __init__(self, reason, message):
        super().__init__(message if message else reason)
        self.reason = reason

class ClientError(APIException):
    """Class for catching 4xx errors"""
    pass

class BadRequest(ClientError):
    """Error code 400: Client provided incorrect parameters for the request."""
    pass

class Forbidden(ClientError):
    """Error code 403: Access denied, either because of missing/incorrect credentials or used API token does not grant access to the requested resource."""
    pass

class NotFound(ClientError):
    """Error code 404: Resource was not found."""
    pass

class TooManyRequests(ClientError):
    """Error code 429: Request was throttled, because amount of requests was above the threshold defined for the used API token."""
    pass


class ServerError(APIException):
    """Class for catching 5xx errors"""
    pass

class InternalError(ServerError):
    """Error code 500: Unknown error happened when handling the request."""
    pass

class Maintenance(ServerError):
    """Error code 503: Service is temprorarily unavailable because of maintenance."""
    pass


class InputError(APIException):
    """Class for catching input errors (such as invalid player/club tag)"""
    pass

class InvalidTag(InputError):
    """User inputted invalid tag"""
    pass

def generate_exception(code: int, reason: str, message: str):
    return {
        400: BadRequest,
        403: Forbidden,
        404: NotFound,
        429: TooManyRequests,
        500: InternalError,
        503: Maintenance
    }[code](reason, message)
