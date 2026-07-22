"""
Custom application exceptions.

Centralizing exception types here keeps the service/repository layers
free of HTTP-specific concerns (status codes, HTTPException, etc.).
Each exception is translated to the correct HTTP status code by the
global exception handlers registered in app/main.py.
"""


class InvalidFileTypeError(Exception):
    """Raised when an uploaded file is not a CSV file. Maps to HTTP 400."""

    pass


class InvalidCSVError(Exception):
    """Raised when a CSV file cannot be parsed (malformed/empty/corrupt). Maps to HTTP 400."""

    pass


class MissingColumnsError(Exception):
    """Raised when a CSV file is missing one or more required columns. Maps to HTTP 422."""

    def __init__(self, missing_columns: list[str]):
        self.missing_columns = missing_columns
        super().__init__(f"Missing required columns: {', '.join(missing_columns)}")
