"""An implementation of the Entity Component System (ECS) paradigm."""

from itertools import repeat as _repeat

__version__ = '1.2.0'

class CommandBuffer():
    """A buffer that stores commands and plays them back later.

    *New in version 1.1.*
    """

    def __init__(self, scene):
        """Associate the buffer with the provided scene."""
        self.scene = scene
        self.commands = []
        self.lasteid = 0
        self.eidmap = {}

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.flush()

    def new(self, *comps):
        """Returns an entity id that is only valid to use with the current buffer. If one or more components are supplied to the method, these will be added to the new entity.

        *New in version 1.2.*
        """

        self.lasteid -= 1
        self.commands.append((self.scene.new, (self.lasteid, *comps,)))

        return self.lasteid

    def add(self, eid, *comps):
        """Add a component to an entity. The component will not be added immediately, but when the buffer is flushed. In particular, exceptions do not occur when calling this method, but only when the buffer is flushed.

        *Changed in version 1.2:* Added support for multiple components.
        *Deprecated since version 1.2:* Use *set()* instead.
        """

        self.commands.append((self.scene.add, (eid, *comps)))

    def set(self, eid, *comps):
        """Set components of an entity. The componentes will not be set immediately, but when the buffer is flushed. In particular, exception do not ossur when calling this method, but only when the buffer if flushed.

        *New in version 1.2.*
        """

        self.commands.append((self.scene.set, (eid, *comps)))

    def remove(self, eid, *comptypes):
        """Remove a component from an entity. The component will not be removed immediately, but when the buffer is flushed. In particular, exceptions do not occur when calling this method, but only when the buffer is flushed.

        *Changed in version 1.2:* Added support for multiple component types.
        """

        self.commands.append((self.scene.remove, (eid, *comptypes)))

    def free(self, eid):
        """Remove all components of an entity. The components will not be removed immediately, but when the buffer if flushed. In particular, exceptions do not occur when calling this method, but only when the buffer is flushed."""

        self.commands.append((self.scene.free, (eid,)))

    def flush(self):
        """Flush the buffer. This will apply all commands that have been previously stored in the buffer to its associated scene. If any arguments in these commands are faulty, exceptions may arrise."""

        for cmd, args in self.commands:
            if cmd == self.scene.new:
                eid, *comps = args
                realeid = self.scene.new(*comps)
                self.eidmap[eid] = realeid
            else:
                eid, *other = args
                if eid < 0: eid = self.eidmap[eid]
                cmd(eid, *other)
        self.commands.clear()

class Scene():
    """A scene of entities that allows for efficient component management."""

    def __init__(self):
        self.entitymap = {} # {eid: (archetype, index)}
        self.archetypemap = {} # {component type: set(archetype)}
        self.chunkmap = {} # {archetype: ([eid], {component type: [component]})}
        self.lasteid = -1 # the last valid entity id

    def _unpackEntity(self, eid):
        """Internal method to unpack the data of an entity. The entity id must be valid and in entitymap, i.e. the entity must have at least one component."""

        archetype, index = self.entitymap[eid]
        eidlist, comptypemap = self.chunkmap[archetype]

        return archetype, index, eidlist, comptypemap

    def _removeEntity(self, eid):
        """Internal method to remove an entity. The entity id must be valid and in entitymap, i.e. the entity must have at least one component."""

        archetype, index, eidlist, comptypemap = self._unpackEntity(eid)

        # remove the entity by swapping it with another entity, or ...
        if len(eidlist) > 1:
            swapid = eidlist[-1]
            if swapid != eid: # do not replace with self
                self.entitymap[swapid] = (archetype, index)

                eidlist[index] = swapid
                for complist in comptypemap.values():
                    swapcomp = complist[-1]
                    complist[index] = swapcomp

            # remove swaped entity
            eidlist.pop()
            for complist in comptypemap.values():
                complist.pop()
        else: # ... if the archetype container will be empty after this, remove it
            for ct in archetype:
                self.archetypemap[ct].remove(archetype)
                if not self.archetypemap[ct]:
                    del self.archetypemap[ct]
            del self.chunkmap[archetype]

        del self.entitymap[eid]

    def _addEntity(self, eid, compdict):
        """Internal method to add an entity. The entity id must be valid and the component list must be non-empty. Also, there must be a maximum of one component of each type."""

        archetype = frozenset(compdict.keys())
        if archetype in self.chunkmap: # collect unique instance from cache, if possible
            archetype = next(iter(x for x in self.chunkmap if x == archetype))

        # if there is no container for the new archetype, create one
        if archetype not in self.chunkmap:
            # add to chunkmap
            self.chunkmap[archetype] = ([], {ct: [] for ct in archetype})

            # add to archetypemap
            for ct in archetype:
                if ct not in self.archetypemap:
                    self.archetypemap[ct] = set()
                self.archetypemap[ct].add(archetype)

        # add the entity and components to the archetype container
        eidlist, comptypemap = self.chunkmap[archetype]
        eidlist.append(eid)
        for ct, c in compdict.items():
            comptypemap[ct].append(c)

        # make reference to entity in entitymap
        index = len(eidlist) - 1
        self.entitymap[eid] = (archetype, index)

    def buffer(self):
        """Return a new command buffer that is associated to this scene.

        *New in version 1.1.*
        *Deprecated since version 1.2:* Use *CommandBuffer(scene)* instead.
        """

        return CommandBuffer(self)

    def new(self, *comps):
        """Returns a valid and previously unused entity id. If one or more components are supplied to the method, these will be added to the new entity. Raises *ValueError* if trying to add duplicate component types.

        *Changed in version 1.2:* Added the optional *comps* parameter.
        """

        # increment valid entity id
        self.lasteid += 1

        # add components
        if comps:
            compdict = {type(c): c for c in comps}

            # raise ValueError on trying to add duplicate component types
            if len(compdict) < len(comps):
                comptypes = [type(comp) for comp in comps]
                raise ValueError(f"adding duplicate component type(s): {', '.join(str(ct) for ct in comptypes if comptypes.count(ct) > 1)}")

            self._addEntity(self.lasteid, compdict)

        return self.lasteid

    def free(self, eid):
        """Remove all components of an entity. The entity id will not be invalidated by this operation. Returns a list of the components. Raises *KeyError* if the entity id is not valid."""

        # raise KeyError on invalid entity id
        if eid < 0 or eid > self.lasteid:
            raise KeyError(f"invalid entity id: {eid}")

        # entity has no components
        if eid not in self.entitymap:
            return []

        _, index, _, comptypemap = self._unpackEntity(eid)

        # collect the components and remove the entity
        components = [comptypemap[comptype][index] for comptype in comptypemap]
        self._removeEntity(eid)

        return components


    def components(self, eid):
        """Returns a tuple of all components of an entity. Raises *KeyError* if the entity id is not valid."""

        # raise KeyError on invalid entity id
        if eid < 0 or eid > self.lasteid:
            raise KeyError(f"invalid entity id: {eid}")

        # entity has no components
        if eid not in self.entitymap:
            return ()

        _, index, _, comptypemap = self._unpackEntity(eid)

        return tuple(comptypemap[comptype][index] for comptype in comptypemap)


    def archetype(self, eid):
        """Returns the archetype of an entity. Raises *KeyError* if the entity id is not valid."""

        # raise KeyError on invalid entity id
        if eid < 0 or eid > self.lasteid:
            raise KeyError(f"invalid entity id: {eid}")

        # entity has no components
        if eid not in self.entitymap:
            return ()

        archetype, _, _, _ = self._unpackEntity(eid)

        return tuple(archetype)


    def add(self, eid, *comps):
        """Add components to an entity. Returns the component(s) as a list if two or more components are given, or a single component instance if only one component is given. Raises *KeyError* if the entity id is not valid or *ValueError* if the entity would have one or more components of the same type after this operation or no components are supplied to the method.

        *Changed in version 1.2:* Added support for multiple components.
        *Deprecated since version 1.2:* Use *set()* instead.
        """

        # raise KeyError on invalid entity id
        if eid < 0 or eid > self.lasteid:
            raise KeyError(f"invalid entity id: {eid}")

        # raise ValueError if no component are given
        if not comps:
            raise ValueError("missing input")

        # raise ValueError if trying to add duplicate component types
        if len(set(type(comp) for comp in comps)) < len(comps):
            comptypes = [type(comp) for comp in comps]
            raise ValueError(f"adding duplicate component type(s): {', '.join(str(ct) for ct in comptypes if comptypes.count(ct) > 1)}")

        complist = list(comps)
        if eid in self.entitymap:
            _, index, _, comptypemap = self._unpackEntity(eid)

            # raise ValueError if trying to add component types that are already present
            if any(type(comp) in comptypemap for comp in comps):
                raise ValueError(f"component type(s) already present: {', '.join(str(type(comp)) for comp in comps if type(comp) in comptypemap)}")

            # collect old components and remove the entity
            complist.extend(comptypemap[comptype][index] for comptype in comptypemap)
            self._removeEntity(eid)

        compdict = {type(c): c for c in complist}
        self._addEntity(eid, compdict)

        if len(comps) == 1:
            return comps[0]
        else:
            return list(comps)

    def set(self, eid, *comps):
        """Set components of an entity. Raises *KeyError* if the entity id is not valid or *ValueError* if trying to set two or more components of the same type simultaneously.

        *New in version 1.2.*
        """

        # raise KeyError on invalid entity id
        if eid < 0 or eid > self.lasteid:
            raise KeyError(f"invalid entity id: {eid}")

        # skip if no components are given
        if not comps:
            return

        # sort components by type
        compdict = {type(comp): comp for comp in comps}

        # raise ValueError if trying to set duplicate component types
        if len(compdict) < len(comps):
            comptypes = list(compdict.keys())
            raise ValueError(f"duplicate component type(s): {', '.join(str(ct) for ct in comptypes if comptypes.count(ct) > 1)}")

        # Modify entity if already presend, else ...
        if eid in self.entitymap:
            _, index, _, comptypemap = self._unpackEntity(eid)
            oldcompdict = {ct: comptypemap[ct][index] for ct in comptypemap}

            # If possible update components directly, else ...
            if compdict.keys() <= oldcompdict.keys():
                for ct, c in compdict.items():
                    comptypemap[ct][index] = c
            else: # ... move entity in into another chunk.
                newcompdict = {**oldcompdict, **compdict}
                self._removeEntity(eid)
                self._addEntity(eid, newcompdict)
        else: # ... add entity.
            self._addEntity(eid, compdict)

    def has(self, eid, *comptypes):
        """Return *True* if the entity has a component of each of the given types, *False* otherwise. Raises *KeyError* if the entity id is not valid or *ValueError* if no component type is supplied to the method.

        *Changed in version 1.2:* Added support for multiple component types.
        """

        # raise KeyError on invalid entity id
        if eid < 0 or eid > self.lasteid:
            raise KeyError(f"invalid entity id: {eid}")

        # raise ValueError if no component types are given
        if not comptypes:
            raise ValueError("missing input")

        # unpack entity
        try:
            archetype, _ = self.entitymap[eid]
            _, comptypemap = self.chunkmap[archetype]
        except KeyError: # eid not in self.entitymap
            return False

        return all(ct in comptypemap for ct in comptypes)

    def collect(self, eid, *comptypes):
        """Collect multiple components of an entity. Returns a list of the components. Raises *KeyError* if the entity id is not valid or *ValueError* if a component of any of the requested types is missing.

        *New in version 1.2.*
        """

        # raise KeyError on invalid entity id
        if eid < 0 or eid > self.lasteid:
            raise KeyError(f"invalid entity id: {eid}")

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


    def get(self, eid, comptype):
        """Get one component of an entity. Returns the component. Raises *KeyError* if the entity id is not valid or *ValueError* if the entity does not have a component of the requested type."""

        # raise KeyError on invalid entity id
        if eid < 0 or eid > self.lasteid:
            raise KeyError(f"invalid entity id: {eid}")

        # unpack entity
        try:
            archetype, index = self.entitymap[eid]
            _, comptypemap = self.chunkmap[archetype]
        except KeyError: # eid not in self.entitymap
            raise ValueError(f"missing component type: {str(comptype)}")

        # collect and return component
        try:
            return comptypemap[comptype][index]
        except KeyError: # comptype not in comptypemap
            raise ValueError(f"missing component type: {str(comptype)}")

    def remove(self, eid, *comptypes):
        """Remove components from an entity. Returns a list of the components if two or more component types are given, or a single component instance if only one component type is given. Raises *KeyError* if the entity id is not valid or *ValueError* if the entity does not have a component of any of the given types or if no component types are supplied to the method.

        *Changed in version 1.2:* Added support for multiple component types.
        """

        # raise KeyError on invalid entity id
        if eid < 0 or eid > self.lasteid:
            raise KeyError(f"invalid entity id: {eid}")

        # raise ValueError if no component types are given
        if not comptypes:
            raise ValueError("missing input")

        # unpack entity
        try:
            archetype, index = self.entitymap[eid]
            _, comptypemap = self.chunkmap[archetype]
        except KeyError: # eid not in self.entitymap
            raise ValueError(f"missing component type(s): {', '.join(str(ct) for ct in comptypes)}")

        # raise ValueError if the entity does not have the requested component types
        if not all(ct in comptypemap for ct in comptypes):
            raise ValueError(f"missing component type(s): {', '.join(str(ct) for ct in comptypes if ct not in comptypemap)}")

        # collect components that will remain on the entity and the ones to be removed
        compdict = {ct: comptypemap[ct][index] for ct in comptypemap if ct not in comptypes}
        removed = list(comptypemap[ct][index] for ct in comptypes)

        # remove the entity and add it back if there are remaining components
        self._removeEntity(eid)
        if compdict:
            self._addEntity(eid, compdict)

        if len(removed) == 1:
            return removed[0]
        else:
            return removed


    def start(self, *systems, **kwargs):
        """Initialize the scene. All systems must implement an `onStart(scene, **kwargs)` method where this scene instance will be passed as the first argument and the `kwargs` of this method will also be passed on. The systems will be called in the same order they are supplied to this method."""

        for system in systems:
            system.onStart(self, **kwargs)

    def update(self, *systems, **kwargs):
        """Update the scene. All systems must implement an `onUpdate(scene, **kwargs)` method where this scene instance will be passed as the first argument and the `kwargs` of this method will also be passed on. The systems will be called in the same order they are supplied to this method."""

        for system in systems:
            system.onUpdate(self, **kwargs)

    def stop(self, *systems, **kwargs):
        """Clean up the scene. All systems must implement an 'onStop(scene, **kwargs)' method where this scene instance will be passed as the first argument and the `kwargs` of this method will also be passed on. The systems will be called in the same order they are supplied to this method."""

        for system in systems:
            system.onStop(self, **kwargs)


    def select(self, *comptypes, exclude=None):
        """Iterate over entity ids and their corresponding components. Yields tuples of the form `(eid, (compA, compB, ...))` where `compA`, `compB`, ... are of the given component types and belong to the entity with entity id eid. If no component types are given, iterate over all entities. If *exclude* is not *None*, entities with component types listed in *exclude* will not be considered. Raises *ValueError* if *exclude* contains component types that are also explicitly included."""

        # raise ValueError if trying to exclude component types that are also included
        if exclude and any(ct in exclude for ct in comptypes):
            raise ValueError(f"excluding explicitely included component types: {', '.join(str(x) for x in set(comptypes).intersection(exclude))}")

        # collect archetypes that should be included and archetypes that should be excluded
        incarchetypes = set.intersection(*[self.archetypemap.get(ct, set()) for ct in comptypes]) if comptypes else set(self.chunkmap.keys())
        excarchetypes = set.union(*[self.archetypemap.get(ct, set()) for ct in exclude]) if exclude else set()

        # iterate over all included archetype that are not excluded
        archetypes = incarchetypes - excarchetypes
        if comptypes:
            for archetype in archetypes:
                eidlist, comptypemap = self.chunkmap[archetype]
                complists = [comptypemap[ct] for ct in comptypes]
                yield from zip(eidlist, zip(*complists))
        else:
            for archetype in archetypes:
                eidlist, _ = self.chunkmap[archetype]
                yield from zip(eidlist, _repeat(()))
