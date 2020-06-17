# Changelog

All notable changes to this project will be documented in this file. This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

- **unreleased**
  - Improve performance of `scene.select()`.
  - Improve performance of `scene.set()`, in the case where the component type is already present and the component will be replaced.
  - Improve performance of `scene.get()`.
  - Improve performance of `scene.collect()`.
  - Improve performance of `scene.remove()`.
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
