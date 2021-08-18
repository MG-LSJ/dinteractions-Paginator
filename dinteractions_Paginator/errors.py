import logging

class PaginatorError(Exception):
    """Base class for exceptions"""

class BadContent(PaginatorError):
    def __init__(self, content):
        super().__init__(f"Content must be a string or list of strings, not {type(content)}!")

class IncorrectDataType(PaginatorError):
    def __init__(self, name, data, var):
        super().__init__(f"Incorrect data type passed in for parameter {name}; should be {data}, not {var}!")

class BadEmoji(PaginatorError):
    def __init__(self, num):
        if num == 1:
            name = "firstEmoji"
        if num == 2:
            name = "prevEmoji"
        if num == 3:
            name = "nextEmoji"
        if num == 4:
            name = "lastEmoji"
        super().__init__(f"{name} needs to be an emoji!")

class TooManyButtons(PaginatorError):
    def __init__(self):
        super().__init__("Too many buttons! Please remove some!")

class PaginatorWarning(Warning):
    """Base class for warnings"""

class BadButtons(PaginatorWarning):
    def __init__(self, msg):
        self.logger = logging.getLogger("dinteractions_Paginator")
        self.logger.warning(msg)

class BadOnly(PaginatorWarning):
    def __init__(self):
        self.logger = logging.getLogger("dinteractions_Paginator")
        self.logger.warning("authorOnly and onlyFor can not both be defined! Using onlyFor instead.")
