import sys, time, argparse, random
import itertools
from mecs import Scene, CommandBuffer
import mecs

try:
    import esper
except ImportError:
    print("WARNING: For running benchmarks on the 'esper' backend, install the necessary package.")

def mean(values):
    """Calculate sample mean."""

    return sum(values) / len(values)

def variance(values, mean):
    """Calculate sample variance."""

    return sum(map(lambda v: (v - mean)**2, values)) / len(values)

class A(): pass
class B(): pass
class C(): pass
class D(): pass
class E(): pass

def mecs_setup_none(hparams):
    """Return an empty scene."""

    return Scene()

def mecs_setup_empty(hparams):
    """Setup a scene with empty entities."""

    scene = Scene()
    eids = [scene.new() for _ in range(hparams.count)]

    return scene, eids

def mecs_setup_A(hparams):
    """Setup a scene with entities that have (A) components."""

    scene = Scene()
    eids = [scene.new(A()) for _ in range(hparams.count)]

    return scene, eids

def mecs_setup_ABC(hparams):
    """Setup a scene with entities that have (ABC) components."""

    scene = Scene()
    eids = [scene.new(A(), B(), C()) for _ in range(hparams.count)]

    return scene, eids

def mecs_setup_ABCDE(hparams):
    """Setup a scene with entities that have (ABCDE) components."""

    scene = Scene()
    eids = [scene.new(A(), B(), C(), D(), E()) for _ in range(hparams.count)]

    return scene, eids

def mecs_setup(hparams):
    """Setup a scene with entities that have (AB), (ABC), (CDE), (DE) component sets."""

    scene = Scene()
    ab = [scene.new(A(), B()) for _ in range(hparams.count // 4)]
    abc = [scene.new(A(), B(), C()) for _ in range(hparams.count // 4)]
    cde = [scene.new(C(), D(), E()) for _ in range(hparams.count // 4)]
    de = [scene.new(D(), E()) for _ in range(hparams.count // 4)]

    return scene, (ab, abc, cde, de)

def mecs_create_empty(scene, hparams):
    for _ in range(hparams.count):
        scene.new()

def mecs_create_A(scene, hparams):
    for _ in range(hparams.count):
        scene.new(A())

def mecs_create_ABC(scene, hparams):
    for _ in range(hparams.count):
        scene.new(A(), B(), C())

def mecs_create_ABCDE(scene, hparams):
    for _ in range(hparams.count):
        scene.new(A(), B(), C(), D(), E())

def mecs_query_all(setup, hparams):
    scene, _ = setup
    for _ in scene.select():
        pass

def mecs_query_A(setup, hparams):
    scene, _ = setup
    for _ in scene.select(A):
        pass

def mecs_query_ABC(setup, hparams):
    scene, _ = setup
    for _ in scene.select(A, B, C):
        pass

def mecs_query_ABCDE(setup, hparams):
    scene, _ = setup
    for _ in scene.select(A, B, C, D, E):
        pass

def mecs_add_A(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.set(eid, A())

def mecs_add_ABC(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.set(eid, A(), B(), C())

def mecs_add_ABCDE(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.set(eid, A(), B(), C(), D(), E())

def mecs_overwrite_A(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.set(eid, A())

def mecs_overwrite_ABC(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.set(eid, A(), B(), C())

def mecs_overwrite_ABCDE(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.set(eid, A(), B(), C(), D(), E())

def mecs_has_A(setup, hparams):
    scene, eids = setup
    for eid in itertools.chain(*eids):
        scene.has(eid, A)

def mecs_has_ABC(setup, hparams):
    scene, eids = setup
    for eid in itertools.chain(*eids):
        scene.has(eid, A, B, C)

def mecs_has_ABCDE(setup, hparams):
    scene, eids = setup
    for eid in itertools.chain(*eids):
        scene.has(eid, A, B, C, D, E)

def mecs_get_A(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.get(eid, A)

def mecs_get_ABC(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.collect(eid, A, B, C)

def mecs_get_ABCDE(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.collect(eid, A, B, C, D, E)

def mecs_remove_A(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.remove(eid, A)

def mecs_remove_ABC(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.remove(eid, A, B, C)

def mecs_remove_ABCDE(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.remove(eid, A, B, C, D, E)

def mecs_query_remove_A(setup, hparams):
    scene, _ = setup
    with CommandBuffer(scene) as buffer:
        for eid, _ in scene.select(A):
            buffer.remove(eid, A)

def mecs_query_remove_ABC(setup, hparams):
    scene, _ = setup
    with CommandBuffer(scene) as buffer:
        for eid, _ in scene.select(A, B, C):
            buffer.remove(eid, A, B, C)

def mecs_destroy(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.free(eid)

def mecs_query_destroy_all(setup, hparams):
    scene, eids = setup
    with CommandBuffer(scene) as buffer:
        for eid, _ in scene.select():
            buffer.free(eid)

def mecs_query_destroy_A(setup, hparams):
    scene, eids = setup
    with CommandBuffer(scene) as buffer:
        for eid, _ in scene.select(A):
            buffer.free(eid)

def mecs_query_destroy_ABC(setup, hparams):
    scene, eids = setup
    with CommandBuffer(scene) as buffer:
        for eid, _ in scene.select(A, B, C):
            buffer.free(eid)

def mecs_archetype(setup, hparams):
    scene, eids = setup
    for eid in itertools.chain(*eids):
        scene.archetype(eid)

def mecs_components(setup, hparams):
    scene, eids = setup
    for eid in itertools.chain(*eids):
        scene.components(eid)

def esper_setup_none(hparams):
    """Setup a world with no entities."""

    return esper.World()

def esper_setup_empty(hparams):
    """Setup a world with empty entities."""

    world = esper.World()
    eids = [world.create_entity() for _ in range(hparams.count)]

    return world, eids

def esper_setup(hparams):
    """Setup a world with entities that have (AB), (ABC), (CDE), (DE) component sets."""

    world = esper.World()
    ab = [world.create_entity(A(), B()) for _ in range(hparams.count // 4)]
    abc = [world.create_entity(A(), B(), C()) for _ in range(hparams.count // 4)]
    cde = [world.create_entity(C(), D(), E()) for _ in range(hparams.count // 4)]
    de = [world.create_entity(D(), E()) for _ in range(hparams.count // 4)]

    return world, (ab, abc, cde, de)

def esper_setup_A(hparams):
    """Setup a world with entities that have (A) components."""

    world = esper.World()
    eids = [world.create_entity(A()) for _ in range(hparams.count)]

    return world, eids

def esper_setup_ABC(hparams):
    """Setup a world with entities that have (ABC) components."""

    world = esper.World()
    eids = [world.create_entity(A(), B(), C()) for _ in range(hparams.count)]

    return world, eids

def esper_setup_ABCDE(hparams):
    """Setup a world with entities that have (ABCDE) components."""

    world = esper.World()
    eids = [world.create_entity(A(), B(), C(), D(), E()) for _ in range(hparams.count)]

    return world, eids

def esper_create_empty(world, hparams):
    for _ in range(hparams.count):
        world.create_entity()

def esper_create_A(world, hparams):
    for _ in range(hparams.count):
        world.create_entity(A())

def esper_create_ABC(world, hparams):
    for _ in range(hparams.count):
        world.create_entity(A(), B(), C())

def esper_create_ABCDE(world, hparams):
    for _ in range(hparams.count):
        world.create_entity(A(), B(), C(), D(), E())

def esper_query_A(setup, hparams):
    world, _ = setup
    for _ in world.get_component(A):
        pass

def esper_query_ABC(setup, hparams):
    world, _ = setup
    for _ in world.get_components(A, B, C):
        pass

def esper_query_ABCDE(setup, hparams):
    world, _ = setup
    for _ in world.get_components(A, B, C, D, E):
        pass

def esper_add_A(setup, hparams):
    world, eids = setup
    for eid in eids:
        world.add_component(eid, A())

def esper_add_ABC(setup, hparams):
    world, eids = setup
    for eid in eids:
        world.add_component(eid, A())
        world.add_component(eid, B())
        world.add_component(eid, C())

def esper_add_ABCDE(setup, hparams):
    world, eids = setup
    for eid in eids:
        world.add_component(eid, A())
        world.add_component(eid, B())
        world.add_component(eid, C())
        world.add_component(eid, D())
        world.add_component(eid, E())

def esper_overwrite_A(setup, hparams):
    world, eids = setup
    for eid in eids:
        world.add_component(eid, A())

def esper_overwrite_ABC(setup, hparams):
    world, eids = setup
    for eid in eids:
        world.add_component(eid, A())
        world.add_component(eid, B())
        world.add_component(eid, C())

def esper_overwrite_ABCDE(setup, hparams):
    world, eids = setup
    for eid in eids:
        world.add_component(eid, A())
        world.add_component(eid, B())
        world.add_component(eid, C())
        world.add_component(eid, D())
        world.add_component(eid, E())

def esper_has_A(setup, hparams):
    world, eids = setup
    for eid in itertools.chain(*eids):
        world.has_component(eid, A)

def esper_has_ABC(setup, hparams):
    world, eids = setup
    for eid in itertools.chain(*eids):
        world.has_components(eid, A, B, C)

def esper_has_ABCDE(setup, hparams):
    world, eids = setup
    for eid in itertools.chain(*eids):
        world.has_components(eid, A, B, C, D, E)

def esper_get_A(setup, hparams):
    world, eids = setup
    for eid in eids:
        world.component_for_entity(eid, A)

def esper_get_ABC(setup, hparams):
    world, eids = setup
    for eid in eids:
        world.component_for_entity(eid, A)
        world.component_for_entity(eid, B)
        world.component_for_entity(eid, C)

def esper_get_ABCDE(setup, hparams):
    world, eids = setup
    for eid in eids:
        world.component_for_entity(eid, A)
        world.component_for_entity(eid, B)
        world.component_for_entity(eid, C)
        world.component_for_entity(eid, D)
        world.component_for_entity(eid, E)

def esper_remove_A(setup, hparams):
    world, eids = setup
    for eid in eids:
        world.remove_component(eid, A)

def esper_remove_ABC(setup, hparams):
    world, eids = setup
    for eid in eids:
        world.remove_component(eid, A)
        world.remove_component(eid, B)
        world.remove_component(eid, C)

def esper_remove_ABCDE(setup, hparams):
    world, eids = setup
    for eid in eids:
        world.remove_component(eid, A)
        world.remove_component(eid, B)
        world.remove_component(eid, C)
        world.remove_component(eid, D)
        world.remove_component(eid, E)

def esper_destroy(setup, hparams):
    world, eids = setup
    for eid in eids:
        world.delete_entity(eid, immediate=True)

def esper_components(setup, hparams):
    world, eids = setup
    for eid in itertools.chain(*eids):
        world.components_for_entity(eid)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--backend", dest="backend", default=None, type=str,
            help="The backends to benchmark, separated by comma.")
    parser.add_argument("-t", "--task", dest="task", default=None, type=str,
            help="The tasks to benchmark, separated by comma.")
    parser.add_argument("-c", "--count", dest="count", default=10**5, type=int,
            help="The number of entities to benchmark (default 10**5).")
    parser.add_argument("-r", "--retries", dest="retries", type=int, default=10,
            help="How many retries for each individual benchmark (default 10).")
    hparams = parser.parse_args()

    mecs_backend = ("mecs", mecs.__version__)
    esper_backend = ("esper", esper.version)

    benchmarks = [
        # backend_name, task_name,    specific,setup_method,      benchmark_method
        (mecs_backend,  "create",     "empty", mecs_setup_none,   mecs_create_empty),
        (mecs_backend,  "create",     "A",     mecs_setup_none,   mecs_create_A),
        (mecs_backend,  "create",     "ABC",   mecs_setup_none,   mecs_create_ABC),
        (mecs_backend,  "create",     "ABCDE", mecs_setup_none,   mecs_create_ABCDE),
        (mecs_backend,  "query",      "all",   mecs_setup,        mecs_query_all),
        (mecs_backend,  "query",      "A",     mecs_setup,        mecs_query_A),
        (mecs_backend,  "query",      "ABC",   mecs_setup,        mecs_query_ABC),
        (mecs_backend,  "query",      "ABCDE", mecs_setup,        mecs_query_ABCDE),
        (mecs_backend,  "add",        "A",     mecs_setup_empty,  mecs_add_A),
        (mecs_backend,  "add",        "ABC",   mecs_setup_empty,  mecs_add_ABC),
        (mecs_backend,  "add",        "ABCDE", mecs_setup_empty,  mecs_add_ABCDE),
        (mecs_backend,  "overwrite",  "A",     mecs_setup_A,      mecs_overwrite_A),
        (mecs_backend,  "overwrite",  "ABC",   mecs_setup_ABC,    mecs_overwrite_ABC),
        (mecs_backend,  "overwrite",  "ABCDE", mecs_setup_ABCDE,  mecs_overwrite_ABCDE),
        (mecs_backend,  "has",        "A",     mecs_setup,        mecs_has_A),
        (mecs_backend,  "has",        "ABC",   mecs_setup,        mecs_has_ABC),
        (mecs_backend,  "has",        "ABCDE", mecs_setup,        mecs_has_ABCDE),
        (mecs_backend,  "get",        "A",     mecs_setup_A,      mecs_get_A),
        (mecs_backend,  "get",        "ABC",   mecs_setup_ABC,    mecs_get_ABC),
        (mecs_backend,  "get",        "ABCDE", mecs_setup_ABCDE,  mecs_get_ABCDE),
        (mecs_backend,  "remove",     "A",     mecs_setup_ABCDE,  mecs_remove_A),
        (mecs_backend,  "remove",     "ABC",   mecs_setup_ABCDE,  mecs_remove_ABC),
        (mecs_backend,  "remove",     "ABCDE", mecs_setup_ABCDE,  mecs_remove_ABCDE),
        (mecs_backend,  "query_remove",     "A", mecs_setup_ABCDE,  mecs_query_remove_A),
        (mecs_backend,  "query_remove",     "ABC", mecs_setup_ABCDE,  mecs_query_remove_ABC),
        (mecs_backend,  "destroy",    "empty", mecs_setup_empty,  mecs_destroy),
        (mecs_backend,  "destroy",    "A",     mecs_setup_A,      mecs_destroy),
        (mecs_backend,  "destroy",    "ABC",   mecs_setup_ABC,    mecs_destroy),
        (mecs_backend,  "destroy",    "ABCDE", mecs_setup_ABCDE,  mecs_destroy),
        (mecs_backend,  "query_destroy",    "all", mecs_setup_ABCDE,  mecs_query_destroy_all),
        (mecs_backend,  "query_destroy",    "A", mecs_setup_ABCDE,  mecs_query_destroy_A),
        (mecs_backend,  "query_destroy",    "ABC", mecs_setup_ABCDE,  mecs_query_destroy_ABC),
        (mecs_backend,  "archetype",  "",      mecs_setup,        mecs_archetype),
        (mecs_backend,  "components", "",      mecs_setup,        mecs_components),

        (esper_backend, "create",     "empty", esper_setup_none,  esper_create_empty),
        (esper_backend, "create",     "A",     esper_setup_none,  esper_create_A),
        (esper_backend, "create",     "ABC",   esper_setup_none,  esper_create_ABC),
        (esper_backend, "create",     "ABCDE", esper_setup_none,  esper_create_ABCDE),
        (esper_backend, "query",      "A",     esper_setup,       esper_query_A),
        (esper_backend, "query",      "ABC",   esper_setup,       esper_query_ABC),
        (esper_backend, "query",      "ABCDE", esper_setup,       esper_query_ABCDE),
        (esper_backend, "add",        "A",     esper_setup_empty, esper_add_A),
        (esper_backend, "add",        "ABC",   esper_setup_empty, esper_add_ABC),
        (esper_backend, "add",        "ABCDE", esper_setup_empty, esper_add_ABCDE),
        (esper_backend, "overwrite",  "A",     esper_setup_A,     esper_overwrite_A),
        (esper_backend, "overwrite",  "ABC",   esper_setup_ABC,   esper_overwrite_ABC),
        (esper_backend, "overwrite",  "ABCDE", esper_setup_ABCDE, esper_overwrite_ABCDE),
        (esper_backend, "has",        "A",     esper_setup,       esper_has_A),
        (esper_backend, "has",        "ABC",   esper_setup,       esper_has_ABC),
        (esper_backend, "has",        "ABCDE", esper_setup,       esper_has_ABCDE),
        (esper_backend, "get",        "A",     esper_setup_A,     esper_get_A),
        (esper_backend, "get",        "ABC",   esper_setup_ABC,   esper_get_ABC),
        (esper_backend, "get",        "ABCDE", esper_setup_ABCDE, esper_get_ABCDE),
        (esper_backend, "remove",     "A",     esper_setup_ABCDE, esper_remove_A),
        (esper_backend, "remove",     "ABC",   esper_setup_ABCDE, esper_remove_ABC),
        (esper_backend, "remove",     "ABCDE", esper_setup_ABCDE, esper_remove_ABCDE),
        #(esper_backend, "destroy",    "empty", esper_setup_empty, esper_destroy),
        (esper_backend, "destroy",    "A",     esper_setup_A,     esper_destroy),
        (esper_backend, "destroy",    "ABC",   esper_setup_ABC,   esper_destroy),
        (esper_backend, "destroy",    "ABCDE", esper_setup_ABCDE, esper_destroy),
        (esper_backend, "components", "",      esper_setup,       esper_components)
        ]

    backends = hparams.backend.split(",") if hparams.backend is not None else None
    tasks = hparams.task.split(",") if hparams.task is not None else None

    for (backend, task, specific, setup, benchmark) in benchmarks:
        backend_name, backend_version = backend
        if backends is not None and backend_name not in backends: continue
        if tasks is not None and task not in tasks: continue

        print(f"{backend_name} ({backend_version})/{task}/{specific}: ", end="", flush=True)

        times = []
        for _ in range(hparams.retries):
            print(".", end="", flush=True)

            s = setup(hparams)

            start = time.process_time()
            benchmark(s, hparams)
            end = time.process_time()

            times.append(end - start)

        m = mean(times)
        print()
        print(f"  mean: {m:<8f}s var: {variance(times, m):<8f}s min: {min(times):<8f}s max: {max(times):<8f}s")
        print()

if __name__ == "__main__":
    main()
