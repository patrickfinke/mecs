"""An implementation of the Entity Component System (ECS) paradigm."""

__version__ = '1.0.0'

class Scene():
    def __init__(self):
        self.entitymap = {} # {eid: (archetype, index)}
        self.archetypemap = {} # {component type: set(archetype)}
        self.chunkmap = {} # {archetype: ([eid], {component type: [component]})}

        self.lasteid = -1

    def _getNewArchetype(self, archetype):
        newarchetype = tuple(sorted(archetype, key = lambda ct: id(ct)))
        if newarchetype not in self.chunkmap:
            return newarchetype
        return next(iter(x for x in self.chunkmap if x == newarchetype)) # find in cache

    def _processBuffers(self):
        pass


    def new(self):
        """Returns a valid and previously unused entity id."""

        self.lasteid += 1
        return self.lasteid

    def free(self, eid):
        """Remove all components of an entity. The entity id will not be invalidated by this operation. Returns a list of the components. Raises KeyError if the entity id is not valid."""

        # invalid entity id
        if eid > self.lasteid:
            raise KeyError()

        # entity has no components
        if eid not in self.entitymap:
            return []

        archetype, index = self.entitymap[eid]
        chunk = self.chunkmap[archetype]
        eidlist, comptypemap = chunk

        # save components and return them later
        components = [comptypemap[comptype][index] for comptype in archetype]

        # prepare replacement entity
        if len(eidlist) > 1:
            swapid = eidlist[-1]
            if swapid != eid: # do not replace with self
                self.entitymap[swapid] = (archetype, index)

                # replace in eid list
                eidlist[index] = swapid

                # replace in every component list
                for complist in comptypemap.values():
                    swapcomp = complist[-1]
                    complist[index] = swapcomp

            eidlist.pop()
            for complist in comptypemap.values():
                complist.pop()
        else: # remove archetype
            for ct in archetype:
                self.archetypemap[ct].remove(archetype)
                if not self.archetypemap[ct]:
                    del self.archetypemap[ct]
            del self.chunkmap[archetype]

        # remove from entitymap
        del self.entitymap[eid]

        return components


    def components(self, eid):
        """Returns a tuple of all components of an entity. Raises KeyError if the entity id is not valid."""

        # invalid entity id
        if eid > self.lasteid:
            raise KeyError()

        # entity has no components
        if eid not in self.entitymap:
            return ()

        archetype, index = self.entitymap[eid]
        chunk = self.chunkmap[archetype]
        _, comptypemap = chunk
        return tuple(comptypemap[comptype][index] for comptype in archetype)


    def archetype(self, eid):
        """Returns the archetype of an entity. Raises KeyError if the entity id is not valid."""

        # invalid entity id
        if eid > self.lasteid:
            raise KeyError()

        # entity has no components
        if eid not in self.entitymap:
            return ()

        archetype, _ = self.entitymap[eid]
        return archetype


    def add(self, eid, comp):
        """Add a component to an entity. Returns the component. Raises KeyError if the entity id is not valid or ValueError if the entity already has a component of the same type."""

        comptype = type(comp)

        # invalid entity id
        if eid > self.lasteid:
            raise KeyError()

        # remove from old archetype
        if eid in self.entitymap:
            archetype, index = self.entitymap[eid]
            if comptype in archetype: # already has component of that type
                raise ValueError()

            chunk = self.chunkmap[archetype]
            eidlist, comptypemap = chunk

            # save components
            components = {ct: comptypemap[ct][index] for ct in archetype}

            # prepare replacement entity
            if len(eidlist) > 1:
                swapid = eidlist[-1]
                if swapid != eid: # do not replace with self
                    self.entitymap[swapid] = (archetype, index)

                    # replace in eid list
                    eidlist[index] = swapid

                    # replace in every component list
                    for complist in comptypemap.values():
                        swapcomp = complist[-1]
                        complist[index] = swapcomp

                eidlist.pop()
                for complist in comptypemap.values():
                    complist.pop()
            else: # remove archetype
                for ct in archetype:
                    self.archetypemap[ct].remove(archetype)
                    if not self.archetypemap[ct]:
                        del self.archetypemap[ct]
                del self.chunkmap[archetype]
        else:
            archetype, index = (), 0
            components = {}
            self.entitymap[eid] = (archetype, index)

        # calculate new archetype
        newarchetype = self._getNewArchetype(archetype + (comptype,))

        # get new chunk
        if newarchetype not in self.chunkmap:
            self.chunkmap[newarchetype] = ([], {ct: [] for ct in newarchetype})

            # add new archetype to archetypemap
            for ct in newarchetype:
                if ct not in self.archetypemap:
                    self.archetypemap[ct] = set()
                self.archetypemap[ct].add(newarchetype)
        newchunk = self.chunkmap[newarchetype]
        neweidlist, newcomptypemap = newchunk

        # add eid to chunk
        neweidlist.append(eid)

        # add old and new components to chunk
        components[comptype] = comp # add new component
        for ct, c in components.items():
            newcomptypemap[ct].append(c)

        # calculate new index and adjust entry in entitymap
        newindex = len(neweidlist) - 1
        self.entitymap[eid] = (newarchetype, newindex)

        return comp

    def has(self, eid, comptype):
        """Return True if the entity has a component of the given type, False otherwise. Raises KeyError if the entity id is not valid."""

        # invalid entity id
        if eid > self.lasteid:
            raise KeyError()

        # entity has no components
        if eid not in self.entitymap:
            return False

        archetype, _ = self.entitymap[eid]
        return comptype in archetype

    def get(self, eid, comptype):
        """Get a component from an entity. Returns the component. Raises KeyError if the entity id is not valid or ValueError if the entity has no component of the given type."""

        # invalid entity id
        if eid > self.lasteid:
            raise KeyError()

        # entity has no components
        if eid not in self.entitymap:
            raise ValueError()

        # component type not part of archetype
        archetype, index = self.entitymap[eid]
        if comptype not in archetype:
            raise ValueError()

        chunk = self.chunkmap[archetype]
        _, comptypemap = chunk
        complist = comptypemap[comptype]
        return complist[index]

    def remove(self, eid, comptype):
        """Remove a component from an entity. Returns the component. Raises KeyError if the entity id is not valid or ValueError if the entity has no component of the given type."""

        # invalid entity id
        if eid > self.lasteid:
            raise KeyError()

        # entity has no components
        if eid not in self.entitymap:
            raise ValueError()

        archetype, index = self.entitymap[eid]
        if comptype not in archetype: # entity has no component of that type
            raise ValueError()

        chunk = self.chunkmap[archetype]
        eidlist, comptypemap = chunk

        # save components
        components = {ct: comptypemap[ct][index] for ct in archetype}

        # prepare replacement entity
        if len(eidlist) > 1:
            swapid = eidlist[-1]
            if swapid != eid: # do not replace with self
                self.entitymap[swapid] = (archetype, index)

                # replace in eid list
                eidlist[index] = swapid

                # replace in every component list
                for complist in comptypemap.values():
                    swapcomp = complist[-1]
                    complist[index] = swapcomp

            eidlist.pop()
            for complist in comptypemap.values():
                complist.pop()
        else: # remove archetype
            for ct in archetype:
                self.archetypemap[ct].remove(archetype)
                if not self.archetypemap[ct]:
                    del self.archetypemap[ct]
            del self.chunkmap[archetype]

        # calculate new archetype
        newarchetype = self._getNewArchetype((ct for ct in archetype if ct is not comptype))

        # get new chunk
        if newarchetype not in self.chunkmap:
            self.chunkmap[newarchetype] = ([], {ct: [] for ct in newarchetype})

            # add new archetype to archetypemap
            for ct in newarchetype:
                if ct not in self.archetypemap:
                    self.archetypemap[ct] = set()
                self.archetypemap[ct].add(newarchetype)
        newchunk = self.chunkmap[newarchetype]
        neweidlist, newcomptypemap = newchunk

        # add eid to chunk
        neweidlist.append(eid)

        # add old components to chunk except the one to be removed
        comp = components[comptype] # remember component
        del components[comptype] # remove component
        for ct, c in components.items():
            newcomptypemap[ct].append(c)

        # calculate new index and adjust entry in entitymap
        newindex = len(neweidlist) - 1
        self.entitymap[eid] = (newarchetype, newindex)

        return comp


    def init(self, *systems, **kwargs):
        """Initialize the scene. All systems must implement an 'init(self, scene, **kwargs)' method where this Scene instance will be passed as the first argument and the **kwargs of this method will also be passed on. The systems will be called in the same order they are supplied to this method."""

        self._processBuffers()
        for system in systems:
            system.init(self, **kwargs)
            self._processBuffers()

    def update(self, *systems, **kwargs):
        """Update the scene. All systems must implement an 'update(self, scene, **kwargs)' method where this Scene instance will be passed as the first argument and the **kwargs of this method will also be passed on. The systems will be called in the same order they are supplied to this method."""

        self._processBuffers()
        for system in systems:
            system.update(self, **kwargs)
            self._processBuffers()

    def destroy(self, *systems, **kwargs):
        """Destroy the scene. All systems must implement an 'destroy(self, scene, **kwargs)' method where this Scene instance  will be passed as the first argument and the **kwargs of this method will also be passed on. The systems will be called in the same order they are supplied to this method."""

        self._processBuffers()
        for system in systems:
            system.destroy(self, **kwargs)
            self._processBuffers()


    def filter(self, *comptypes, exclude=None):
        """Iterate over entity ids and their corresponding components. Yields tuples of the form (eid, (compA, compB, ...)) where compA, compB, ... are of the given component types and belong to the entity with entity id eid. If no component types are given, iterate over all entities. If exclude is not None, entities with component types listed in exclude will not be returned. Raises ValueError if exclude component types that are explicitly requested."""

        if exclude and any(ct in exclude for ct in comptypes):
            raise ValueError()

        incarchetypes = set.intersection(*[self.archetypemap.get(ct, set()) for ct in comptypes]) if comptypes else set(self.chunkmap.keys())
        excarchetypes = set.union(*[self.archetypemap.get(ct, set()) for ct in exclude]) if exclude else set()

        archetypes = incarchetypes - excarchetypes
        for archetype in archetypes:
            chunk = self.chunkmap[archetype]
            eidlist, comptypemap = chunk
            if comptypes:
                complists = [comptypemap[ct] for ct in comptypes]
                for eid, comps in zip(eidlist, zip(*complists)):
                    yield eid, comps
            else:
                for eid in eidlist:
                    yield eid, ()
