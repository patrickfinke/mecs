from .entity import _generate_new_entity_id

class CommandBuffer():
    """
    A buffer that stores commands and plays them back later.

    *New in version 1.1.*
    """

    def __init__(self, storage):
        """
        Associate the buffer with an entity storage.
        """

        self._storage = storage
        self._commands = []

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.flush()

    @property
    def storage(self):
        return self._storage

    def defer_create(self, component=None):
        """
        Store a future call to the *create()* method of the associated storage.

        Returns the entity id of the entity that will be created.

        *New in version 1.2.*
        *Changed in version 1.3:* Entity ids are globally valid.
        """

        entity = _generate_new_entity_id()
        self._commands.append((self._storage.create, (component, entity)))
        
    def defer_destroy(self, entity):
        """
        Store a future call to the *destroy()* method of the associated storage.

        *New in version 1.3.*
        """

        self._commands.append((self._storage.destroy, (entity,)))

    def defer_set(self, entity, component):
        """
        Store a future call to the *set()* method of the associated storage.

        *New in version 1.2.*
        """

        self._commands.append((self._storage.set, (entity, component)))

    def defer_delete(self, entity, component_type):
        """
        Store a future call to the *delete()* method of the associated storage.

        *Changed in version 1.2:* Added support for multiple component types.
        """

        self._commands.append((self._storage.delete, (entity, component_type)))

    def defer_clear(self):
        """
        Storage a future call to the *clear()* method of the accociated storage.

        *New in version 1.3.*
        """

        self._commands.append((self._storage.clear,))

    def flush(self):
        """
        Flush the buffer.

        This will apply all commands that have previously been stored in the buffer to the associated storage. Note that if any of the arguments in these commands were invalid, exceptions may arrise.
        """

        for cmd, args in self._commands:
            cmd(*args)
        self.clear()

    def clear(self):
        """
        Clear the buffer.

        This does not apply any of the stored commands.

        *New in version 1.3.*
        """

        self._commands.clear()

