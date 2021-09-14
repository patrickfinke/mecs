"""An implementation of the Entity Component System (ECS) paradigm."""

from uuid import uuid4 as _generate_new_entity_id
from itertools import repeat as _repeat

__version__ = '1.2.1'

class _Container():
    """
    A container for entities with the same signature.

    This class does not check its inputs for errors and should only be used internally.
    """
    
    def __init__(self, signature):
        self._signature = signature
        self._entities = []
        self._components = {ct: [] for ct in self._signature}
        self._indices = {}

    def __len__(self):
        """
        Return the number of entities in the container.
        """

        return len(self._entities)

    def __iter__(self):
        """
        Iterate over all entities in the container.
        """

        yield from self._entities

    @property
    def signature(self):
        """
        Return the (shared) signature of all entities in the container.
        """

        return self._signature

    @property
    def entities(self):
        """
        Return a list of all entities in the container.
        """

        return self._entities

    def component_list(self, component_type):
        """
        Return a list of all components of a type.
        """

        return self._components[component_type]

    def add(self, entity, component_dict):
        """
        Add an entity to the container.
        """

        self._entities.append(entity)

        for component_type, component in component_dict.items():
            self._components[component_type].append(component)

        index = len(self._entities) - 1
        self._indices[entity] = index

        return index

    def _move(self, index_to, index_from):
        """
        Overwrite the entity data at one index with the entity data form another index.
        """

        self._entities[index_to] = self._entities[index_from]

        for component_list in self._components.values():
            component_list[index_to] = component_list[index_from]

        entity_from = self._entities[index_from]
        self._indices[entity_from] = index_to

    def remove(self, entity):
        """
        Remove an entity form the container.
        """

        index = self._indices[entity]

        last_index = len(self._entities) - 1
        if index != last_index:
            moved_entity, moved_index_to = self._move(index, last_index)

        self._entities.pop()

        for component_list in self._components.values():
            component_list.pop()

        del self._indices[entity]

    def component_dict(self, entity):
        """
        Return the component dict of an entity.

        The component dict maps component types to component instances.
        """

        index = self._indices[entity]

        component_dict = {ct: cl[index] for ct, cl in self._components.items()}
        return component_dict

    def component(self, entity, component_type):
        """
        Return a component of an entitiy.
        """

        index = self._indices[entity]
        component_list = self._components[component_type]
        component = component_list[index]
        return component

    def update(self, entity, component_dict):
        """
        Set components of an entity.
        """

        index = self._indices[entity]

        for component_type, component in component_dict.items():
            component_list = self._components[component_type]
            component_list[index] = component

class Filter():
    """
    A filter that can be matched against signatures.

    *New in version 1.3.*
    """

    def __init__(self, single_filter, group_filter):
        self._single_filter = single_filter
        self._group_filter = group_filter

    def __and__(self, other):
        """
        Return a new filter that matches a signature if that signature matches this filter and the other filter.
        """

        single_filter = lambda signature: self._single_filter(signature) and other._single_filter(signature)
        group_filter = lambda archetypemap: self._group_filter(archetypemap) & other._group_filter(archetypemap)
        return Filter(single_filter, group_filter)

    def __or__(self, other):
        """
        Return a new filter that matches a signature if that signature matches this filter or the other filter.
        """

        singled_filter = lambda signature: self._single_filter(signature) or other._single_filter(signature)
        group_filter = lambda archetypemap: self._group_filter(archetypemap) | other._group_filter(archetypemap)
        return Filter(singled_filter, group_filter)

    def __invert__(self):
        """
        Return a new filter that matches a signature if that signature does not match this filter.
        """

        singled_filter = lambda signature: not self._single_filter(signature)
        group_filter = lambda archetypemap: set.union(*archetypemap.values()) - self._group_filter(archetypemap)
        return Filter(singled_filter, group_filter)

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

class CommandBuffer():
    """
    A buffer that stores commands and plays them back later.

    *New in version 1.1.*
    """

    def __init__(self, storage):
        """
        Associate the buffer with an entity storage.
        """

        self.storage = storage
        self.commands = []

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.flush()

    def new(self, *comps):
        """
        Returns an entity id that is only valid to use with the current buffer. If one or more components are supplied to the method, these will be added to the new entity.

        *New in version 1.2.*
        """

        eid = _generate_new_eid()
        self.commands.append((self.storage.set, (eid, *comps,)))

        

    def set(self, eid, *comps):
        """
        Set components of an entity.

        The componentes will not be set immediately, but when the buffer is flushed. In particular, exception do not occur when calling this method, but only when the buffer if flushed.

        *New in version 1.2.*
        """

        self.commands.append((self.storage.set, (eid, *comps)))

    def remove(self, eid, *comptypes):
        """
        Remove a component from an entity.

        The component will not be removed immediately, but when the buffer is flushed. In particular, exceptions do not occur when calling this method, but only when the buffer is flushed.

        *Changed in version 1.2:* Added support for multiple component types.
        """

        self.commands.append((self.storage.remove, (eid, *comptypes)))

    def free(self, eid):
        """
        Remove all components of an entity.

        The components will not be removed immediately, but when the buffer if flushed. In particular, exceptions do not occur when calling this method, but only when the buffer is flushed.
        """

        self.commands.append((self.storage.free, (eid,)))

    def flush(self):
        """
        Flush the buffer.

        This will apply all commands that have been previously stored in the buffer to the associated entity storage. If any arguments in these commands are faulty, exceptions may arrise.
        """

        for cmd, args in self.commands:
            cmd(*args)
        self.commands.clear()

class Storage():
    """
    A storage for entities.

    When a component is added to an entity that is not part of the storage, the entity is automatically added as well. When all components of an entity are removed, the entity is automatically removed from the storage. Thus, the storage contains all entities that have at least one component.
    """

    def __init__(self):
        self._entity_to_container = {} # {entity: container}
        self._ctype_to_container = {} # {component_type: container}
        self._signature_to_container = {} # {signature: container}

    def _add_entity(self, entity, component_dict):
        """
        Adds an entity to the storage.

        Adds the entity to the container that matches the signature and creates the container if it does not already exist. This method does not check its inputs for errors and should only be used internally!
        """

        signature = frozenset(component_dict.keys())

        if not signature in self._signature_to_container:
            container = _Container(signature)

            self._signature_to_container[signature] = container
            for component_type in signature:
                self._ctype_to_container.setdefault(component_type, set()).add(container)
        else:
            container = self._signature_to_container[signature]

        self._entity_to_container[entity] = container
        container.add(entity, component_dict)

    def _remove_entity(self, entity):
        """
        Remove an entity from the storage.

        Remove an entity from its container and delete the container if it is empty after the entity is removed. This method does not check its inputs for errors and should only be used internally.
        """

        container = self._entity_to_container[entity]

        del self._entity_to_container[entity]
        container.remove(entity)

        if not container:
            signature = container.signature

            del self._signature_to_container[signature]
            for component_type in signature:
                self._ctype_to_container[component_type].remove(container)
                if not self._ctype_to_container[component_type]:
                    del self._ctype_to_container[component_type]

    def _update_entity(self, entity, component_dict):
        """
        Set components of an entity.

        If the entity does not have a component of the specified type it is added, otherwise the old component is replaced. The container of the entity is only changed when the signature changes. This method does not check its inputs for errors and should only be used internally.
        """

        container = self._entity_to_container[entity]
        signature = container.signature

        if component_dict.keys() <= signature:
            container.update(entity, component_dict)
        else:
            entity_component_dict = container.component_dict(entity)
            entity_component_dict.update(component_dict)
            self._remove_entity(entity)
            self._add_entity(entity, entity_component_dict)

    @property
    def storage(self):
        return self

    def __bool__(self):
        """
        Check if the storage is not empty.

        An entity is in the storage if it has at least one component.
        """

        return bool(self._entity_to_container)

    def __len__(self):
        """
        Return the number of entities in the storage.

        An entity is in the storage if it has at least one component.
        """

        return len(self._entity_to_container)

    def __contains__(self):
        """
        Check if an entity is in the storage.

        An entity is in the storage if it has at least one component.
        """

        return entity in self._entity_to_container

    def __iter__(self):
        """
        Iterate over all entities in the storage.

        An entity is in the storage if it has at least one component.
        """

        for container in self._entity_to_container.values():
            yield from container

    def new(self, *components):
        """
        Generate a new entity id.

        Generates a previously unused entity id and returns it. If any components are passed to this method, the last of every type will be added to the entity.

        *Changed in version 1.2:* Added the optional *comps* parameter.
        *Changed in version 1.3:* Sets the last component of a type instead of raising *ValueError*.
        """

        entity = _generate_new_entity_id()
        self.set(entity, *components)
        return entity

    def free(self, entity):
        """
        Remove all components from an entity.

        If the entity does not have any components this method does nothing.

        *Changed in version 1.3:* Exit silently instead of raising *KeyError* and return `None` instead of the components.
        """

        if entity in self._entity_to_container:
            self._remove_entity(entity)

    def components(self, entity):
        """
        Return a list of all components of an entity.

        *Changed in version 1.3:* Return `[]` instead of raising `KeyError` and return a list instead of a tuple.
        """

        try:
            container = self._entity_to_container[entity]
        except KeyError:
            return []

        components = list(container.component_dict(entity).values())
        return components

    def signature(self, entity):
        """
        Return the signature of an entity.

        *Changed in version 1.3:* Renamed from `archetype` and return a frozenset instead of a tuple.
        """

        try:
            container = self._entity_to_container[entity]
        except KeyError:
            return frozenset()

        signature = container.signature
        return signature

    def set(self, entity, *components):
        """
        Set components of an entity.

        If the entity already has a component of the same type it gets replaced, otherwise the component is added. If multiple components of the same type are passed, the last one prevails.

        *New in version 1.2.*
        *Changed in version 1.3:* Does not raise *KeyError* or *ValueError* anymore.
        """

        if not components:
            return

        component_dict = {type(c): c for c in components}
        if entity in self._entity_to_container:
            self._update_entity(entity, component_dict)
        else:
            self._add_entity(entity, component_dict)

    def match(self, entity, filter):
        """
        Match the signature of an entity with a filter.

        Return *True* if the signature of the entity matches the filter, *False* otherwise.

        *New in version 1.3.*
        """

        try:
            container = self._entity_to_container[entity]
            signature = container.signature
        except KeyError:
            signature = frozensset()

        return filter._single_filter(signature)

    def collect(self, eid, *comptypes):
        """Collect multiple components of an entity. Returns a list of the components. Raises *KeyError* if the entity id is not valid or *ValueError* if a component of any of the requested types is missing.

        *New in version 1.2.*
        """

        # return empty list if no components are requested
        if not comptypes:
            return []

        # unpack entity
        try:
            archetype, index = self.entitymap[eid]
            _, comptypemap = self.chunkmap[archetype]
        except KeyError: # eid not in self.entitymap
            raise ValueError(f"missing component type(s): {', '.join(str(ct) for ct in comptypes)}")

        # collect and return components
        try:
            return [comptypemap[ct][index] for ct in comptypes]
        except KeyError: # ct not in comptypemap
            raise ValueError(f"missing component type(s): {', '.join(str(ct) for ct in comptypes if ct not in comptypemap)}")

    def get(self, entity, component_type):
        """
        Get a component of an entity.

        Returns the component. Raises *KeyError* if the entity does not have a component of the requested type.

        *Changed in version 1.3.* Does not raise *KeyError* on invalid entity id but on invalid component type and does not raise *ValueError* anymore.
        """

        try:
            container = self._entity_to_container[entity]
        except KeyError:
            raise KeyError(component_type)

        try:
            component = container.component(entity, component_type)
        except KeyError:
            raise KeyError(component_type)

        return component

    def unset(entity, *component_types):
        """
        Discard components from an entity.

        If the entity has a component of the given type it gets removed, if it does not have one nothing happends.

        *New in version 1.3.*
        """

        if not component_types:
            return

        try:
            container = self._entity_to_container[entity]
        except KeyError:
            return

        component_types = set(component_types)
        signature = container.signature
        if not signature & component_types:
            return

        component_dict = container.component_dict(entity)
        self._remove_entity(entity)

        new_component_dict = {ct: c for ct, c in component_dict.items() if ct not in component_types}
        if new_component_dict:
            self._add_entity(entity, new_component_dict)

    def start(self, *systems, **kwargs):
        """
        Initialize the scene.

        All systems must implement an `onStart(scene, **kwargs)` method where this scene instance will be passed as the first argument and the `kwargs` of this method will also be passed on. The systems will be called in the same order they are supplied to this method.
        """

        for system in systems:
            system.onStart(self, **kwargs)

    def update(self, *systems, **kwargs):
        """
        Update the scene.

        All systems must implement an `onUpdate(scene, **kwargs)` method where this scene instance will be passed as the first argument and the `kwargs` of this method will also be passed on. The systems will be called in the same order they are supplied to this method.
        """

        for system in systems:
            system.onUpdate(self, **kwargs)

    def stop(self, *systems, **kwargs):
        """Clean up the scene.

        All systems must implement an 'onStop(scene, **kwargs)' method where this scene instance will be passed as the first argument and the `kwargs` of this method will also be passed on. The systems will be called in the same order they are supplied to this method.
        """

        for system in systems:
            system.onStop(self, **kwargs)

    def select(self, *component_types):
        """
        Iterate over entities and their components.

        Yields pairs *(entity, components)* where *components* is a list of components that belong to *entity* and with types as specified in *component_types*. Raises *KeyError* if one of the entities does not have all the required component types.
        """

        containers = set.union(*self._ctype_to_container.values())
        for container in containers:
            if component_types:
                try:
                    components = [container.component_list(ct) for ct in component_types]
                except KeyError:
                    raise KeyError(component_types)
            else:
                components = [([] for _ in range(len(container))]
            yield from zip(container, zip(*components))

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
                components = [([] for _ in range(len(container))]
            yield from zip(container, zip(*components))
