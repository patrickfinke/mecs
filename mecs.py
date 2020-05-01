"""An implementation of the Entity Component System (ECS) paradigm."""

__version__ = '1.1.0'

class CommandBuffer():
    """A buffer that stores commands and plays them back later."""
    def __init__(self, scene):
        self.scene = scene
        self.commands = []
        self.lasteid = 0
        self.eidmap = {}

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.flush()

    def new(self, *comps):
        """Returns an entity id that is only valid to use with the current buffer. If one or more components are supplied to the method, these will be added to the new entity."""

        self.lasteid -= 1

        self.commands.append((self.scene.new, (self.lasteid, *comps,)))

        return self.lasteid

    def add(self, eid, *comps):
        """Add a component to an entity. The component will not be added immediately, but when the buffer is flushed. In particular, exceptions do not occur when calling this method, but only when the buffer is flushed."""
        self.commands.append((self.scene.add, (eid, *comps)))

    def remove(self, eid, *comptypes):
        """Remove a component from an entity. The component will not be removed immediately, but when the buffer is flushed. In particular, exceptions do not occur when calling this method, but only when the buffer is flushed."""
        self.commands.append((self.scene.remove, (eid, *comptypes)))

    def free(self, eid):
        """Remove all components of an entity. The components will not be removed immediately, but when the buffer if flushed. In particular, exceptions do not occur when calling this method, but only when the buffer is flushed."""
        self.commands.append((self.scene.free, (eid,)))

    def flush(self):
        """Flush the buffer. This will apply all commands that have been previously added to the buffer. If any arguments in these commands are faulty, exceptions may arrise."""
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
    def __init__(self):
        self.entitymap = {} # {eid: (archetype, index)}
        self.archetypemap = {} # {component type: set(archetype)}
        self.chunkmap = {} # {archetype: ([eid], {component type: [component]})}
        self.lasteid = -1 # the last valid entity id

    def _getArchetype(self, comptypelist):
        """Internal method to get the unique (in memory) archetype tuple that corresponds to the passed list of component types. No component type must appear more than once."""

        newarchetype = tuple(sorted(comptypelist, key = lambda ct: id(ct)))
        if newarchetype not in self.chunkmap:
            return newarchetype
        return next(iter(x for x in self.chunkmap if x == newarchetype)) # find in cache

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

    def _addEntity(self, eid, complist):
        """Internal method to add an entity. The entity id must be valid and the component list must be non-empty. Also, there must be a maximum of one component of each type."""

        # calculate new archetype
        archetype = self._getArchetype((type(comp) for comp in complist))

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
        for c in complist:
            comptypemap[type(c)].append(c)

        # make reference to entity in entitymap
        index = len(eidlist) - 1
        self.entitymap[eid] = (archetype, index)

    def buffer(self):
        """Return a new command buffer for this scene."""

        return CommandBuffer(self)

    def new(self, *comps):
        """Returns a valid and previously unused entity id. If one or more components are supplied to the method, these will be added to the new entity. Raise ValueError if trying to add duplicate component types."""

        # increment valid entity id
        self.lasteid += 1

        # add components
        if comps:
            # raise ValueError on trying to add duplicate component types
            if len(set(type(comp) for comp in comps)) < len(comps):
                comptypes = [type(comp) for comp in comps]
                raise ValueError(f"adding duplicate component type(s): {', '.join(str(ct) for ct in comptypes if comptypes.count(ct) > 1)}")

            self._addEntity(self.lasteid, comps)

        return self.lasteid

    def free(self, eid):
        """Remove all components of an entity. The entity id will not be invalidated by this operation. Returns a list of the components. Raises KeyError if the entity id is not valid."""

        # raise KeyError on invalid entity id
        if eid > self.lasteid:
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
        """Returns a tuple of all components of an entity. Raises KeyError if the entity id is not valid."""

        # raise KeyError on invalid entity id
        if eid > self.lasteid:
            raise KeyError(f"invalid entity id: {eid}")

        # entity has no components
        if eid not in self.entitymap:
            return ()

        _, index, _, comptypemap = self._unpackEntity(eid)

        return tuple(comptypemap[comptype][index] for comptype in comptypemap)


    def archetype(self, eid):
        """Returns the archetype of an entity. Raises KeyError if the entity id is not valid."""

        # raise KeyError on invalid entity id
        if eid > self.lasteid:
            raise KeyError(f"invalid entity id: {eid}")

        # entity has no components
        if eid not in self.entitymap:
            return ()

        archetype, _, _, _ = self._unpackEntity(eid)

        return archetype


    def add(self, eid, *comps):
        """Add components to an entity. Returns the component(s) as a list if two or more components are given, or a single component instance if only one component is given. Raises KeyError if the entity id is not valid or ValueError if the entity would have one or more components of the same type after this operation or no components are supplied to the method."""

        # raise KeyError on invalid entity id
        if eid > self.lasteid:
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

        self._addEntity(eid, complist)

        if len(comps) == 1:
            return comps[0]
        else:
            return list(comps)

    def has(self, eid, *comptypes):
        """Return True if the entity has a component of each of the given types, False otherwise. Raises KeyError if the entity id is not valid or ValueError if no component type is supplied to the method."""

        # raise KeyError on invalid entity id
        if eid > self.lasteid:
            raise KeyError(f"invalid entity id: {eid}")

        # raise ValueError if no component types are given
        if not comptypes:
            raise ValueError("missing input")

        # entity has no components
        if eid not in self.entitymap:
            return False

        _, _, _, comptypemap = self._unpackEntity(eid)

        return all(ct in comptypemap for ct in comptypes)

    def get(self, eid, *comptypes):
        """Get components from an entity. Returns a list of the components if two or more component types are given, or a single component instance if only one component type is given. Raises KeyError if the entity id is not valid or ValueError if a component of any of the given types is missing or if no component types are supplied to the method."""

        # raise KeyError on invalid entity id
        if eid > self.lasteid:
            raise KeyError(f"invalid entity id: {eid}")

        # raise ValueError if no component types are given
        if not comptypes:
            raise ValueError("missing input")

        # raise ValueError if the entity does not have any components
        if eid not in self.entitymap:
            raise ValueError(f"missing component type(s): {', '.join(str(ct) for ct in comptypes)}")

        _, index, _, comptypemap = self._unpackEntity(eid)

        # raise ValueError if the entity does not have the requested component types
        if not all(ct in comptypemap for ct in comptypes):
            raise ValueError(f"missing component type(s): {', '.join(str(ct) for ct in comptypes if ct not in comptypemap)}")

        if len(comptypes) == 1:
            return comptypemap[comptypes[0]][index]
        else:
            return [comptypemap[ct][index] for ct in comptypes]

    def remove(self, eid, *comptypes):
        """Remove components from an entity. Returns a list of the components if two or more component types are given, or a single component instance if only one component type is given. Raises KeyError if the entity id is not valid or ValueError if the entity does not have a component of any of the given types or if no component types are supplied to the method."""

        # raise KeyError on invalid entity id
        if eid > self.lasteid:
            raise KeyError(f"invalid entity id: {eid}")

        # raise ValueError if no component types are given
        if not comptypes:
            raise ValueError("missing input")

        # raise ValueError if the entity does not have any components
        if eid not in self.entitymap:
            raise ValueError(f"missing component type(s): {', '.join(str(ct) for ct in comptypes)}")

        _, index, _, comptypemap = self._unpackEntity(eid)

        # raise ValueError if the entity does not have the requested component types
        if not all(ct in comptypemap for ct in comptypes):
            raise ValueError(f"missing component type(s): {', '.join(str(ct) for ct in comptypes if ct not in comptypemap)}")

        # collect components that will remain on the entity and the ones to be removed
        remaining = list(comptypemap[ct][index] for ct in comptypemap if ct not in comptypes)
        removed = list(comptypemap[ct][index] for ct in comptypes)

        # remove the entity and add it back if there are remaining components
        self._removeEntity(eid)
        if remaining:
            self._addEntity(eid, remaining)

        if len(removed) == 1:
            return removed[0]
        else:
            return removed


    def start(self, *systems, **kwargs):
        """Initialize the scene. All systems must implement an 'onStart(scene, **kwargs)' method where this scene instance will be passed as the first argument and the **kwargs of this method will also be passed on. The systems will be called in the same order they are supplied to this method."""

        for system in systems:
            system.onStart(self, **kwargs)

    def update(self, *systems, **kwargs):
        """Update the scene. All systems must implement an 'onUpdate(self, scene, **kwargs)' method where this scene instance will be passed as the first argument and the **kwargs of this method will also be passed on. The systems will be called in the same order they are supplied to this method."""

        for system in systems:
            system.onUpdate(self, **kwargs)

    def stop(self, *systems, **kwargs):
        """Clean up the scene. All systems must implement an 'onStop(self, scene, **kwargs)' method where this scene instance will be passed as the first argument and the **kwargs of this method will also be passed on. The systems will be called in the same order they are supplied to this method."""

        for system in systems:
            system.onStop(self, **kwargs)


    def select(self, *comptypes, exclude=None):
        """Iterate over entity ids and their corresponding components. Yields tuples of the form (eid, (compA, compB, ...)) where compA, compB, ... are of the given component types and belong to the entity with entity id eid. If no component types are given, iterate over all entities. If exclude is not None, entities with component types listed in exclude will not be returned. Raises ValueError if exclude contains component types that are also explicitly included."""

        # raise ValueError if trying to exclude component types that are also included
        if exclude and any(ct in exclude for ct in comptypes):
            raise ValueError(f"excluding explicitely included component types: {', '.join(str(x) for x in set(comptypes).intersection(exclude))}")

        # collect archetypes that should be included and archetypes that should be excluded
        incarchetypes = set.intersection(*[self.archetypemap.get(ct, set()) for ct in comptypes]) if comptypes else set(self.chunkmap.keys())
        excarchetypes = set.union(*[self.archetypemap.get(ct, set()) for ct in exclude]) if exclude else set()

        # iterate over all included archetype that are not excluded
        archetypes = incarchetypes - excarchetypes
        for archetype in archetypes:
            eidlist, comptypemap = self.chunkmap[archetype]
            # yield in the right format
            if comptypes:
                complists = [comptypemap[ct] for ct in comptypes]
                for eid, comps in zip(eidlist, zip(*complists)):
                    yield eid, comps
            else:
                for eid in eidlist:
                    yield eid, ()
