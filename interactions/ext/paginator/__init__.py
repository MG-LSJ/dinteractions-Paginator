"""
dinteractions-Paginator

- ButtonKind
- Data
- Page
- Paginator
- StopPaginator
"""

from .errors import StopPaginator
from .paginator import ButtonKind, Data, Page, Paginator

__all__ = ["ButtonKind", "Data", "Page", "Paginator", "StopPaginator"]
