"""
yaecs - Yet another Entity Component System
"""

from .entity import Entity
from .component import Component
from .storage import Storage, Signature
from .view import View
from .command_buffer import CommandBuffer
from .filter import Filter
from .error import EntityError, ComponentError

__all__ = [
    "Entity",
    "Component",
    "Storage",
    "Signature",
    "View",
    "CommandBuffer",
    "Filter",
    "EntityError",
    "ComponentError"
]

__version_info__ = (1, 2, 1)
__version__ = ".".join(str(x) for x in __version_info__)
