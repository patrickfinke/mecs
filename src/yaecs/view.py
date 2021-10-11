class View():
    """
    A view of an entity storage (or anothe view) that only shows entities that are part of the underlying storage (or view) and match a given filter.

    *New in version 1.3.*
    """

    def __init__(self, storage_or_view, filter):
        self._storage = storage_or_view.storage

        if isinstance(storage_or_view, View):
            self._filter = filter & storage_or_view.filter
        else:
            self._filter = filter

    def _matching_containers(self):
        """
        Yield all containers which signatures match the filter.
        """

        container_map = self._storage._ctype_to_container
        containers = self._filter._group_filter(container_map)
        yield from containers

    @property
    def storage(self):
        """
        The entity storage.
        """

        return self._storage

    @property
    def filter(self):
        """
        The filter.
        """

        return self._filter

    def __bool__(self):
        """
        Check if at least one entity in the storage matches the filter.
        """

        for container in self._matching_containers():
            return True
        return False

    def __len__(self):
        """
        Return the number of entities in the storage that match the filter.
        """

        return sum(len(container) for container in self._matching_containers())

    def __contains__(self):
        """
        Check if a entity is in the storage and matches the filter.
        """

        if not entity in self._storage:
            return False

        signature = self._storage.signature(entity)
        match = self._filter._single_filter(signature)
        return match

    def __iter__(self):
        """
        Iterate over all entities in the storage that match the filter.
        """

        for container in self._matching_containers():
            yield from container

    def select(self, *component_types):
        """
        Iterate over entities and their components.

        Yields pairs *(entity, components)* where *components* is a list of components that belong to *entity* and with types as specified in *component_types*. Raises *KeyError* if one of the entities does not have all the required component types.
        """

        for container in self._matching_containers():
            if component_types:
                try:
                    components = [container.component_list(ct) for ct in component_types]
                except KeyError:
                    raise KeyError(component_types)
            else:
                components = [([] for _ in range(len(container)))]
            yield from zip(container, zip(*components))
