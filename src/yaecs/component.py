from .filter import Filter

class ComponentMeta(type, Filter):
    """
    Metaclass for components.

    *New in version 1.3.*
    """

    def __init__(self, *args, **kwargs):
        single_filter = lambda signature: self in signature
        group_filter = lambda archetypemap: archetypemap.get(self, set())
        Filter.__init__(self, single_filter, group_filter)

class Component(metaclass=ComponentMeta):
    """
    Base class from which all components must inherit.

    *New in version 1.3.*
    """

    pass

