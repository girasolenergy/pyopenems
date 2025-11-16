"""openems.exceptions."""


class APIError(Exception):
    """OpenEMS API error with error code."""

    def __init__(self, message: str, code: int):
        """Initialize APIError.

        Args:
            message: Error message describing the error.
            code: Numeric error code from the API.
        """
        super().__init__(message)
        self.code = code
