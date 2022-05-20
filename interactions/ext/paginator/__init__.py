"""
dinteractions-Paginator

- ButtonKind
- Data
- Page
- Paginator
- StopPaginator
"""

from .errors import StopPaginator
from .extension import base, version
from .paginator import ButtonKind, Data, Page, Paginator

__all__ = ["ButtonKind", "Data", "Page", "Paginator", "StopPaginator", "base", "version"]
