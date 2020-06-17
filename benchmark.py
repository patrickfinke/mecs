import sys, time, argparse, random
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

class Position():
    def __init__(self, x=0.0, y=0.0):
        self.x, self.y = x, y

class Velocity():
    def __init__(self, x=0.0, y=0.0):
        self.x, self.y = x, y

class Lifetime():
    def __init__(self, timer=1.0):
        self.timer = timer

def mecs_setup_none(hparams):
    return Scene()

def mecs_setup_empty(hparams):
    scene = Scene()
    eids = []
    for _ in range(hparams.count):
        eid = scene.new()
        eids.append(eid)
    return scene, eids

def mecs_setup_partial(hparams):
    scene = Scene()
    eids = []
    for _ in range(hparams.count):
        position = Position(random.random() * 200 - 100, random.random() * 200 - 100)
        eid = scene.new(position)
        eids.append(eid)
    return scene, eids

def mecs_setup_full(hparams):
    scene = Scene()
    eids = []
    for _ in range(hparams.count):
        position = Position(random.random() * 200 - 100, random.random() * 200 - 100)
        velocity = Velocity(random.random() * 200 - 100, random.random() * 200 - 100)
        lifetime = Lifetime(random.random() * 10 + 5)
        eid = scene.new(position, velocity, lifetime)
        eids.append(eid)
    return scene, eids

def mecs_setup_mixed(hparams):
    scene = Scene()
    eids = []
    for _ in range(hparams.count // 2):
        position = Position(random.random() * 200 - 100, random.random() * 200 - 100)
        velocity = Velocity(random.random() * 200 - 100, random.random() * 200 - 100)
        lifetime = Lifetime(random.random() * 10 + 5)
        eid = scene.new(position, velocity, lifetime)
        eids.append(eid)

        position = Position(random.random() * 200 - 100, random.random() * 200 - 100)
        velocity = Velocity(random.random() * 200 - 100, random.random() * 200 - 100)
        eid = scene.new(position, velocity)
        eids.append(eid)
    return scene, eids


def mecs_create_entities(scene, hparams):
    for _ in range(hparams.count):
        scene.new()

def mecs_create_entities_one_component(scene, hparams):
    for _ in range(hparams.count):
        scene.new(Position())

def mecs_create_entities_two_components(scene, hparams):
    for _ in range(hparams.count):
        scene.new(Position(), Velocity())

def mecs_create_entities_three_components(scene, hparams):
    for _ in range(hparams.count):
        scene.new(Position(), Velocity(), Lifetime())

def mecs_query_all_entities(setup, hparams):
    scene, _ = setup
    for _ in scene.select():
        pass

def mecs_query_one_component(setup, hparams):
    scene, _ = setup
    for _ in scene.select(Position):
        pass

def mecs_query_two_components(setup, hparams):
    scene, _ = setup
    for _ in scene.select(Position, Velocity):
        pass

def mecs_query_three_components(setup, hparams):
    scene, _ = setup
    for _ in scene.select(Position, Velocity, Lifetime):
        pass

def mecs_add_one_component(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.set(eid, Position())

def mecs_add_two_components(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.set(eid, Position(), Velocity())

def mecs_add_three_components(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.set(eid, Position(), Velocity(), Lifetime())

def mecs_overwrite_one_component(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.set(eid, Position())

def mecs_overwrite_two_components(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.set(eid, Position(), Velocity())

def mecs_overwrite_three_components(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.set(eid, Position(), Velocity(), Lifetime())

def mecs_has_one_component(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.has(eid, Position)

def mecs_has_two_components(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.has(eid, Position, Velocity)

def mecs_has_three_components(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.has(eid, Position, Velocity, Lifetime)

def mecs_has_three_components_false(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.has(eid, Position, Velocity, Lifetime)

def mecs_get_one_component(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.get(eid, Position)

def mecs_get_two_components(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.collect(eid, Position, Velocity)

def mecs_get_three_components(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.collect(eid, Position, Velocity, Lifetime)

def mecs_remove_one_component(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.remove(eid, Position)

def mecs_remove_two_components(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.remove(eid, Position, Velocity)

def mecs_remove_three_components(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.remove(eid, Position, Velocity, Lifetime)

def mecs_destroy_zero_components(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.free(eid)

def mecs_destroy_three_components(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.free(eid)

def mecs_archetype_three_components(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.archetype(eid)

def mecs_components_three_components(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.components(eid)

def mecs_example_movement(setup, hparams):
    class MovementSystem():
        def onUpdate(self, scene, deltaTime, **kwargs):
            for eid, (pos, vel) in scene.select(Position, Velocity):
                pos.x += vel.x * deltaTime
                pos.y += vel.y * deltaTime

    scene = Scene()

    systems = [MovementSystem()]

    for _ in range(hparams.count):
        scene.new(Position(random.random() * 200 - 100, random.random() * 200 - 100), Velocity(random.random() * 10 - 5, random.random() * 10 - 5))

    scene.update(*systems, deltaTime=.1)

def esper_setup_empty(hparams):
    world = esper.World()
    eids = []
    for _ in range(hparams.count):
        eid = world.create_entity()
        eids.append(eid)
    return world, eids

def esper_setup_partial(hparams):
    world = esper.World()
    eids = []
    for _ in range(hparams.count):
        eid = world.create_entity(Position(random.random() * 200 - 100, random.random() * 200 - 100))
        eids.append(eid)
    return world, eids

def esper_setup_full(hparams):
    world = esper.World()
    eids = []
    for _ in range(hparams.count):
        position = Position(random.random() * 200 - 100, random.random() * 200 - 100)
        velocity = Velocity(random.random() * 200 - 100, random.random() * 200 - 100)
        lifetime = Lifetime(random.random() * 10 - 5)
        eid = world.create_entity(position, velocity, lifetime)
        eids.append(eid)
    return world, eids

def esper_setup_mixed(hparams):
    world = esper.World()
    eids = []
    for _ in range(hparams.count // 2):
        position = Position(random.random() * 200 - 100, random.random() * 200 - 100)
        velocity = Velocity(random.random() * 200 - 100, random.random() * 200 - 100)
        lifetime = Lifetime(random.random() * 10 - 5)
        eid = world.create_entity(position, velocity, lifetime)
        eids.append(eid)

        position = Position(random.random() * 200 - 100, random.random() * 200 - 100)
        velocity = Velocity(random.random() * 200 - 100, random.random() * 200 - 100)
        eid = world.create_entity(position, velocity)
        eids.append(eid)
    return world, eids


def esper_create_zero_components(setup, hparams):
    world, _ = setup
    for _ in range(hparams.count):
        world.create_entity()

def esper_create_one_component(setup, hparams):
    world, _ = setup
    for _ in range(hparams.count):
        world.create_entity(Position())

def esper_create_two_components(setup, hparams):
    world, _ = setup
    for _ in range(hparams.count):
        world.create_entity(Position(), Velocity())

def esper_create_three_components(setup, hparams):
    world, _ = setup
    for _ in range(hparams.count):
        world.create_entity(Position(), Velocity(), Lifetime())

def esper_query_one_component(setup, hparams):
    world, _ = setup
    for _, _ in world.get_component(Position):
        pass

def esper_query_two_components(setup, hparams):
    world, _ = setup
    for _, _ in world.get_components(Position, Velocity):
        pass

def esper_query_three_components(setup, hparams):
    world, _ = setup
    for _, _ in world.get_components(Position, Velocity, Lifetime):
        pass

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
        # backend_name, task_name, specific_name, setup_method, benchmark_method
        (mecs_backend, "create", "", mecs_setup_none, mecs_create_entities),
        (mecs_backend, "create", "1 component", mecs_setup_none, mecs_create_entities_one_component),
        (mecs_backend, "create", "2 components", mecs_setup_none, mecs_create_entities_two_components),
        (mecs_backend, "create", "3 components", mecs_setup_none, mecs_create_entities_three_components),
        (mecs_backend, "query", "all", mecs_setup_full, mecs_query_all_entities),
        (mecs_backend, "query", "1 component", mecs_setup_full, mecs_query_one_component),
        (mecs_backend, "query", "2 components", mecs_setup_full, mecs_query_two_components),
        (mecs_backend, "query", "3 components", mecs_setup_full, mecs_query_three_components),
        (mecs_backend, "add", "1 component", mecs_setup_empty, mecs_add_one_component),
        (mecs_backend, "add", "2 components", mecs_setup_empty, mecs_add_two_components),
        (mecs_backend, "add", "3 components", mecs_setup_empty, mecs_add_three_components),
        (mecs_backend, "overwrite", "1 component", mecs_setup_full, mecs_overwrite_one_component),
        (mecs_backend, "overwrite", "2 components", mecs_setup_full, mecs_overwrite_two_components),
        (mecs_backend, "overwrite", "3 components", mecs_setup_full, mecs_overwrite_three_components),
        (mecs_backend, "has", "1 component", mecs_setup_full, mecs_has_one_component),
        (mecs_backend, "has", "2 components", mecs_setup_full, mecs_has_two_components),
        (mecs_backend, "has", "3 components", mecs_setup_full, mecs_has_three_components),
        (mecs_backend, "has", "3 components (false)", mecs_setup_full, mecs_has_three_components_false),
        (mecs_backend, "get", "1 component", mecs_setup_full, mecs_get_one_component),
        (mecs_backend, "get", "2 components", mecs_setup_full, mecs_get_two_components),
        (mecs_backend, "get", "3 components", mecs_setup_full, mecs_get_three_components),
        (mecs_backend, "remove", "1 component", mecs_setup_full, mecs_remove_one_component),
        (mecs_backend, "remove", "2 components", mecs_setup_full, mecs_remove_two_components),
        (mecs_backend, "remove", "3 components", mecs_setup_full, mecs_remove_three_components),
        (mecs_backend, "destroy", "0 components", mecs_setup_full, mecs_destroy_zero_components),
        (mecs_backend, "destroy", "3 components", mecs_setup_full, mecs_destroy_three_components),
        (mecs_backend, "archetype", "", mecs_setup_full, mecs_archetype_three_components),
        (mecs_backend, "components", "", mecs_setup_full, mecs_components_three_components),
        (mecs_backend, "example", "movement", mecs_setup_full, mecs_example_movement),

        (esper_backend, "create", "0 components", esper_setup_empty, esper_create_zero_components),
        (esper_backend, "create", "1 component", esper_setup_empty, esper_create_one_component),
        (esper_backend, "create", "2 components", esper_setup_empty, esper_create_two_components),
        (esper_backend, "create", "3 components", esper_setup_empty, esper_create_three_components),
        (esper_backend, "query", "1 component", esper_setup_full, esper_query_one_component),
        (esper_backend, "query", "2 components", esper_setup_full, esper_query_two_components),
        (esper_backend, "query", "3 components", esper_setup_full, esper_query_three_components)
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
