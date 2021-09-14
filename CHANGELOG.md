# Changelog

All notable changes to this project will be documented in this file. This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

- **v1.3 - Filters and Views**

  - Entity IDs are now random UUIDs. In particular, IDs returned by `CommandBuffer.new()` are valid withing the corresponding `Scene` instance.
  - All entity IDs are now considered valid, thus no method will raise a `KeyError` on invalid entity ID. It is left to the user to only use those entity IDs that have been returned by `Scene.new()` or `CommandBuffer.new()`.
  - Removed deprecated methods `Scene.buffer()`, `Scene.add()`, `CommandBuffer.add()`
  - Removed `Scene.has()`, use `Scene.match()` instead.
  - Changed `Scene.new()` so that the last component of every type is added to the new entity instead of raising `ValueError`.
  - Changed `Scene.free()` so that it does not raise `KeyError` anymore and returns `None` instead of the components instead of the components..
  - Changed `Scene.components()` so that it does not raise `KeyError` anymore and returns a list instead of a tuple.
  - Renamed `Scene.archetype()` to `Scene.signature()` and return a frozenset instead of a tuple.
  - Changed `Scene.set()` so that it does not raise `KeyError` or `ValueError` anymore.
  - Changed `Scene.get()` so that it does not raise `ValueError` anymore and does not raise `KeyError` on invalid entity id but on invalid component type.
  - Rename `Scene` to `Storage`.
  - Add `View` to get a filtered view of a `Storage` instance. This replaces and extends the behaviour of `Storage.select()`.
  - Change `Storage.select()` to work like `View.select()`.

- v1.2.1 - Improve performance

  - Improve performance of `Scene.select()`, `Scene.get()`, `Scene.collect()`, `Scene.remove()`, `Scene.free()`, `Scene.has()`, `Scene.components()`, and `Scene.archetype()`. Improve performance of `Scene.set()` in the case where the component type is already present and the component will be replaced.
  - Improve performance of internal methods (improving overall performance).
  - Other changes:
    - Add benchmarks.

- **v1.2.0 - manipulating multiple components at once**

  - Add support for multiple components/component types to `scene.add()`, `scene.has()`, and `scene.remove()` aswell as `CommandBuffer.add()` and `CommandBuffer.remove()`.
  - Add `scene.collect()` to retrieve more than one component at once.
  - Add `scene.set()` for adding and overwriting components.
  - Add support for adding components directly when allocating a new entity id with `scene.new()`.
  - Add `CommandBuffer.new()` as the counterpart to `scene.new()`.
  - Add informative messages to exceptions.
  - Refactor for minor performance increase.
  - Deprecate `scene.add()` in favour of `scene.set()`.
  - Deprecate `scene.buffer()` in favour of `CommandBuffer(scene)`.
  - Fix a typo in `test.py`.

- **v1.1.0 - Add command buffer**

  When using `scene.select()`, manipulation of entities can now be recorded using the `CommandBuffer` instance returned by `scene.buffer()`, and played back at a later time. This avoids unexpected behavior that would occur when using the scene instance directly.

- **v1.0.0 - First release**

  The base functionality is implemented. Note that at this stage it is not safe to add or remove components while iterating over their entities. This will be fixed in a future release.
