class PaginatorError(Exception):
    """Base class for exceptions"""


class StopPaginator(PaginatorError):
    """Exception raised to stop paginator"""


class PaginatorWontWork(PaginatorError):
    """Exception raised when paginator won't work"""
