from logging import getLogger


class PaginatorError(Exception):
    """Base class for exceptions"""


class IncorrectDataType(PaginatorError):
    def __init__(self, name, data, var):
        super().__init__(
            f"Incorrect data type passed in for parameter {name}; should be {data}, not {var}!"
        )


class TooManyButtons(PaginatorError):
    def __init__(self):
        super().__init__("Too many buttons! Please remove some!")


class PaginatorWarning(Warning):
    """Base class for warnings"""


class BadButtons(PaginatorWarning):
    def __init__(self, msg):
        self.logger = getLogger("dinteractions_Paginator")
        self.logger.warning(msg)


class BadOnly(PaginatorWarning):
    def __init__(self):
        self.logger = getLogger("dinteractions_Paginator")
        self.logger.warning(
            "authorOnly and onlyFor can not both be defined! Using onlyFor instead."
        )
