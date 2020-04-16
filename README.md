# mecs

**`mecs` is an implementation of the Entity Component System (ECS) paradigm for Python 3, with a focus on interface minimalism and performance.**

Inspired by [Esper](https://github.com/benmoran56/esper) and Sean Fisk's [ecs](https://github.com/seanfisk/ecs).

### Contents
 - [Changelog](#changelog)
 - [Installation](#installation)
 - [About the ECS paradigm](#ecs-paradigm)
 - [Using `mecs` in your project](#mecs-usage)
    - [Managing entities](#mecs-entities)
    - [Implementing and managing components](#mecs-componentes)
    - [Implementing and running systems](#mecs-systems)
    - [A basic update loop](#mecs-loop)

<a name="changelog"/>

## Changelog
- **v1.0.0 - First release**

  This is the first release of `mecs` where its base functionality is implemented and working. Note that at this stage it is not save to add or remove components while iterating over their entities. This will be fixed in a future release.

<a name="installation"/>

## Installation
`mecs` is implemented in a single file with no dependencies. Simply copy `mecs.py` to your project folder and `import mecs`.

<a name="ecs-paradigm"/>

## About the ECS paradigm

The Entity Component System (ECS) paradigm consists of three different concepts, namely **entities**, **components** and **systems**. These should be understood as follows

1. **Entities** are unique identifiers, labeling a set of components as belonging to a logical group.
2. **Components** are plain data and have no logic associated to them. They define the behavior of entities.
3. **Systems** are logic that operate on entities and their components. They change the behavior of entities by adding, removing and mutation their components.

For more information about the ECS paradigm, visit the [Wikipedia article](https://en.wikipedia.org/wiki/Entity_component_system) or Sander Mertens' [ecs-faq](https://github.com/SanderMertens/ecs-faq).

<a name="mecs-usage"/>

## Using `mecs` in your project
For the management of entities, components and systems, `mecs` provides the `Scene` class. Only entities within the same scene may interact with one another. You can create a new scene with

```python
scene = Scene()
```
<a name="mecs-entities"/>

### Managing entities

Entities are nothing more than unique (integer) identifiers. To get hold of a previously unused **entity id** use

```python
eid = scene.new()
```

<a name="mecs-componentes"/>

### Implementing and managing components

Components can be instances of any class and `mecs` does not provide a base class for them. For example a `Position` component containing `x` and `y` coordinates could look like this

```python
class Position():
  def __init__(self, x, y):
    self.x, self.y = x, y
```

Another example would be a similar `Velocity` component.

```python
class Velocity():
  def __init__(self, vx, vy):
    self.vx, self.vy = vx, vy
```

Note that while these have almost the same structure, replacing both by a more general `TwoValues` component would not be a good idea. `Position` and `Velocity` describe different properties of an object and thus should be kept explicitely separate.

Components are distinguished by their **component type**. To get the type of a component use the build-in `type()`.

```python
position = Position(15, 8)
type(position)
# => <class '__main__.Position'>
```

The `Scene` class provides the following methods for interacting with entities and components. Note that the entity id used in these methods must be valid, i.e. must be returned from `scene.new()`. Using an invalid entity id results in a `KeyError`.

#### 1. Add components using `scene.add(eid, comp)`.

This also returns the component.

```python
scene.add(eid, position)
# => <__main__.Position object at 0x000001EF033E3160>
```

Entities can only have one component of a type. Tying to add another component of the same type results in a `ValueError`. Note that the same component instance can be added to multiple entities, making them share the component data.

#### 2. Check if a component is part of an entity using `scene.has(eid, comptype)`.

```python
scene.has(eid, Position)
# => True
scene.has(eid, Velocity)
# => False
```

#### 3. Modifying components using `scene.get(eid, comptype)`.

This returns the component.

```python
pos = scene.get(eid, Position)
pos.x += 1
```

Tying to get a component type that was not previously added to an entity results in a `ValueError`.

#### 4. Removing components using `scene.remove(eid, comptype)`.

This also returns the component.

```python
scene.remove(eid, Position)
# => <__main__.Position object at 0x000001EF033E3160>
```

#### 5. Removing all components from an entity using `scene.free(eid)`.

This also returns a list of the components.

```python
scene.add(eid, Position())
scene.add(eid, Velocity())
scene.free(eid)
# => [<__main__.Position object at 0x000001EF0358D370>, <__main__.Velocity object at 0x000001EF035B47C0>]
```

Note that this does not make the entity id invalid. In fact, there is no way to invalidate a once valid id. In particular, there is no method to check if an entity is still 'alive'. If you need such behaviour consider attaching an `Alive` component (that has no further data) to every entity that needs it and use `scene.has(eid, Alive)` to determine if the entity is alive.

#### 6. Viewing the archetype of an entity and all of its components using `scene.archetype(eid)` and `scene.components(eid)`.

The **archetype** of an entity is the tuple of all component types that are attached to it.

```python
scene.add(eid, Position(32, 64))
scene.add(eid, Velocity(8, 16))
scene.archetype(eid)
# => (<class '__main__.Position'>, <class '__main__.Velocity'>)
scene.components(eid)
# => (<__main__.Position object at 0x000001EF0358D370>, <__main__.Velocity object at 0x000001EF035B47C0>)
```

The result of `scene.archetype(eid)` is sorted, so comparisons of the form `scene.archetype(eid1) == scene.archetype(eid2)` are safe, but hardly necessary.

#### 7. Iterating over entities and components using `scene.filter(*comptypes, exclude=None)`.

The result of this method is a generator object yielding tuples of the form `(eid, (compA, compB, ...))` where `compA`, `compB` belong to the entity with entity id `eid` and have the requested types. Optionally, an iterable (such as a list or tuple) may be passed to the `exclude` argument, in which case all entities having one or more component types listed in `exclude` will not be yielded by the method.

```python
# adjust position based on velocity
dt = current_deltatime()
for eid, (pos, vel) in scene.filter(Position, Velocity):
  pos.x += vel.vx * dt
  pos.y += vel.vy * dt

# play sounds, remove them if they ended
for eid, (sound,) in scene.filter(Sound):
  if not sound.isPlaying():
    sound.play()
  else if sound.hasEnded():
    scene.remove(eid, Sound)
```

Iterating over entities that have a certain set of components is one of the most important tasks in the ECS paradigm. Usually, this is done by systems to efficiently apply their logic to the appropriate entities. For more examples, visit the section about systems.

<a name="mecs-systems"/>

### Implementing and running systems

As with components, `mecs` does not provide a base class for systems. The `Scene` class has three methods to inject your systems logic.

#### 1. Initialization with `scene.init(*systems, **kwargs)`.

Any instance of any class that implements a method with the signature `init(scene, **kwargs)` may be passed as a valid system. The scene instance will pass itself on via the `scene` argument as well as any `kwargs`. All systems will be called in the order they are passed to this method.

```python
class RenderSystem():
  def init(self, scene, resolution=(600, 480), **kwargs):
    init_graphics_devices(resolution)

renderSystem = RenderSystem()
initsystems = [renderSystem, AnotherInitSystem()]
scene.init(*initsystems, resolution=(1280, 720))
```

#### 2.  Update with `scene.update(*systems, **kwargs)`.

Any instance of any class that implements a method with the signature `update(scene, **kwargs)` may be passed as a valid system. The scene instance will pass itself on via the `scene` argument as well as any `kwargs`. All systems will be called in the order they are passed to this method.

```python
class RenderSystem():
  def update(self, scene, **kwargs):
    for eid, (pos, rend) in scene.filter(Position, Renderable):
      render_at_position(pos.x, pos.y, rend.texture)

class MovementSystem():
  def update(self, scene, dt=1, **kwargs):
    for eid, (pos, vel) in scene.filter(Position, Velocity):
      pos.x += vel.vx * dt
      pos.y += vel.vy * dt

updatesystems = [renderSystem, MovementSystem()]
scene.update(*updatesystems, dt=current_deltatime())
```

#### 3. Destroy with `scene.destroy(*systems, **kwargs)`.

Any instance of any class that implements a method with the signature `destroy(scene, **kwargs)` may be passed as a valid system. The scene instance will pass itself on via the `scene` argument as well as any `kwargs`. All systems will be called in the order they are passed to this method.

```python
class RenderSystem():
  def destroy(self, scene, **kwargs):
    stop_graphics_devices()

destroysystems = [renderSystem, AnotherDestroySystem()]
scene.destroy(*destroysystems)
```

<a name="mecs-loop"/>

### A basic update loop

When trying to write the main loop of your program you may use this pattern.

```python
# Your system instances go here. Be sure to use the same instances
# in different lists if one of your systems implements more than one
# of the init, update or destroy methods.
initsystems = []
updatesystems = []
destroysystems = []

print("[Press Ctrl+C to stop]")
try:
  scene = Scene()
  scene.init(*initsystems)
  while True:
    deltaTime = current_deltatime()
    scene.update(*updatesystems, dt=deltaTime)
except KeyboardInterrupt:
  pass
finally:
  scene.destroy(*destroysystems)
```
