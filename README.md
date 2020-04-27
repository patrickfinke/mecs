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

For a full list of changes see [CHANGELOG.md](CHANGELOG.md).

- **v1.1.0 - Add command buffer**

  When using `scene.select()`, manipulation of entities can now be recorded using the `CommandBuffer` instance returned by `scene.buffer()`, and played back at a later time. This avoids unexpected behavior that would occur when using the scene instance directly.

- **v1.0.0 - First release**

  The base functionality is implemented. Note that at this stage it is not safe to add or remove components while iterating over their entities. This will be fixed in a future release.

<a name="installation"/>

## Installation

`mecs` is implemented in a single file with no dependencies. Simply copy `mecs.py` to your project folder and `import mecs`.

<a name="ecs-paradigm"/>

## About the ECS paradigm

The Entity Component System (ECS) paradigm consists of three different concepts, namely **entities**, **components** and **systems**. These should be understood as follows:

1. **Entities** are unique identifiers, labeling a set of components as belonging to a logical group.
2. **Components** are plain data and implement no logic. They define the behavior of entities.
3. **Systems** are logic that operates on entities and their components. They enforce the appropriate behavior of entities with certain component sets and are also able to change their behavior by adding, removing and mutating components.

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

Components can be instances of any class and `mecs` does not provide a base class for them. For example a `Position` component containing `x` and `y` coordinates could look like this:

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

Components are distinguished by their **component type**. To get the type of a component use the build-in `type()`:

```python
position = Position(15, 8)
type(position)
# => <class '__main__.Position'>
```

\
\
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

Note that this does not make the entity id invalid. In fact, there is no way to invalidate a once valid id. In particular, there is no method to check if an entity is still 'alive'. If you need such behavior, consider attaching an `Alive` component (that has no further data) to every entity that needs it and use `scene.has(eid, Alive)` to determine if the entity is alive.

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

#### 7. Iterating over entities and components using `scene.select(*comptypes, exclude=None)`.

The result of this method is a generator object yielding tuples of the form `(eid, (compA, compB, ...))` where `compA`, `compB` belong to the entity with entity id `eid` and have the requested types. Optionally, an iterable (such as a list or tuple) may be passed to the `exclude` argument, in which case all entities having one or more component types listed in `exclude` will not be yielded by the method.

It is *very important* to note, that between the creation and exhaustion of the generator it is *not* save to use the `scene.add()`, `scene.remove()`, and `scene.free()` methods, as these will alter the structure of the underlying database. Using these methods while iterating over the generator does not raise any exceptions, but will often lead to unexpected behavior! To resolve this issue, `mecs` provides the `CommandBuffer` class, which implements `CommandBuffer.add(eid, comp)`, `CommandBuffer.remove(eid, comptype)`, and `CommandBuffer.free(eid)`. The command buffer will record any calls to these methods, and when it is save to do so, the recordings can be played back to the scene by calling `CommandBuffer.flush()`. Alternatively, the command buffer can be used as a context manager, which is strongly recommended. To get a new `CommandBuffer` instance associated to the scene use `scene.buffer()`.

```python
# adjust position based on velocity
dt = current_deltatime()
for eid, (pos, vel) in scene.select(Position, Velocity):
  pos.x += vel.vx * dt
  pos.y += vel.vy * dt

# play sounds, remove them if they ended
with scene.buffer() as buffer:
  for eid, (sound,) in scene.select(Sound):
    if not sound.isPlaying():
      sound.play()
    elif sound.hasEnded():
      buffer.remove(eid, Sound)
```

Iterating over entities that have a certain set of components is one of the most important tasks in the ECS paradigm. Usually, this is done by systems to efficiently apply their logic to the appropriate entities. For more examples, see the section about systems.

<a name="mecs-systems"/>

### Implementing and running systems

As with components, `mecs` does not provide a base class for systems. Instead, a system should implement any of the three callback methods (`onStart()`, `onUpdate()`, and `onStop()`) and must be passed to the corresponding method of the `Scene` class.

#### 1. Initializing a scene using `scene.start(*systems, **kwargs)`.

Any instance of any class that implements a method with the signature `onStart(scene, **kwargs)` may be used as an input to this method.

The scene iterates through all systems in the order they are passed and calls their respective `onStart()` methods, passing itself using the `scene` argument. Additionally, any `kwargs` will also be passed on.

```python
class RenderSystem():
  def onStart(self, scene, resolution=(600, 480), **kwargs):
    self.graphics = init_graphics_devices(resolution)
    self.textures = load_textures("./resources/textures")

renderSystem = RenderSystem()
startSystems = [renderSystem, AnotherInitSystem()]
scene.start(*startSystems, resolution=(1280, 720))
```

This method should *not* be called multiple times. Instead, all necessary systems should be instantiated first, followed by a single call to `scene.start()`.

#### 2. Updating a scene using `scene.update(*systems, **kwargs)`.

Any instance of any class that implements a method with the signature `onUpdate(scene, **kwargs)` may be used as an input to this method.

The scene iterates through all systems in the order they are passed and calls their respective `onUpdate()` methods, passing itself using the `scene` argument. Additionally, any `kwargs` will also be passed on.

```python
class RenderSystem():
  def onUpdate(self, scene, **kwargs):
    for eid, (pos, rend) in scene.select(Position, Renderable):
      texture = self.textures[rend.textureId]
      self.graphics.render(pos.x, pos.y, texture))

class MovementSystem():
  def onUpdate(self, scene, dt=1, **kwargs):
    for eid, (pos, vel) in scene.select(Position, Velocity):
      pos.x += vel.vx * dt
      pos.y += vel.vy * dt

updateSystems = [MovementSystem(), renderSystem]
scene.update(*updateSystems, dt=current_deltatime())
```

To avoid any unnecessary overhead, call this method only once per update circle, passing all necessary systems as arguments.

#### 3. Cleaning up a scene using `scene.stop(*systems, **kwargs)`.

Any instance of any class that implements a method with the signature `onStop(scene, **kwargs)` may be used as an input to this method.

The scene iterates through all systems in the order they are passed and calls their respective `onStop()` methods, passing itself using the `scene` argument. Additionally, any `kwargs` will also be passed on.

```python
class RenderSystem():
  def onStop(self, scene, **kwargs):
    stop_graphics_devices(self.graphics)
    unload_textures(self.textures)

stopSystems = [renderSystem, AnotherDestroySystem()]
scene.stop(*stopSystems)
```

As with `scene.start()` this method should *not* be called multiple times, but instead once with all the necessary systems.

<a name="mecs-loop"/>

### A basic update loop

When trying to write the main loop of your program you may use this pattern.

```python
# Your system instances go here. Be sure to use the same instances
# in different lists if one of your systems implements more than one
# of the init, update or destroy methods.
startSystems = []
updateSystems = []
stopSystems = []

print("[Press Ctrl+C to stop]")
try:
  scene = Scene()
  scene.start(*startSystems)
  while True:
    deltaTime = current_deltatime()
    scene.update(*updateSystems, dt=deltaTime)
except KeyboardInterrupt:
  pass
finally:
  scene.stop(*stopSystems)
```
