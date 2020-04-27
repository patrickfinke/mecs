# Changelog

All notable changes to this project will be documented in this file. This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

- **unreleased**

  - Add informative messages to exceptions.

- **v1.1.0 - Add command buffer**

  When using `scene.select()`, manipulation of entities can now be recorded using the `CommandBuffer` instance returned by `scene.buffer()`, and played back at a later time. This avoids unexpected behavior that would occur when using the scene instance directly.

- **v1.0.0 - First release**

  The base functionality is implemented. Note that at this stage it is not safe to add or remove components while iterating over their entities. This will be fixed in a future release.
