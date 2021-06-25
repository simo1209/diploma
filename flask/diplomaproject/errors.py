from flask import jsonify

class BaseHTTPException(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


class BadRequest(BaseHTTPException):

    def __init__(self, message, payload=None):
        super().__init__(message, 400, payload)
        

class Unauthorized(BaseHTTPException):

    def __init__(self, message, payload=None):
        super().__init__(message, 401, payload)
        

class Conflict(BaseHTTPException):

    def __init__(self, message, payload=None):
        super().__init__(message, 409, payload)
        


