import sys, time, argparse, random
from mecs import Scene, CommandBuffer

try:
    import esper
except ImportError:
    print("WARNING: For running benchmarks on the 'esper' backend, install the necessary package.")

def mean(values):
    """Calculate the mean value."""

    return sum(values) / len(values)

def benchmark(backend, task, specific, restarts=10, metric=mean, ndigits=4, setup=None):
    """Benchmark a function."""

    def timer(function):
        def wrapper(hparams, verbose=False):
            times = []
            for _ in range(restarts):
                setup_result = setup(hparams) if setup is not None else Scene()

                start = time.process_time()
                function(setup_result, hparams)
                end = time.process_time()
                times.append(end - start)
                
            result = metric(times)
            if verbose:
                print(f"{backend}/{task}/{specific}: {round(result, ndigits)} seconds")
            return result

        wrapper.backend = backend
        wrapper.task = task
        wrapper.specific = specific
        return wrapper
    return timer

class Position():
    def __init__(self, x=0.0, y=0.0):
        self.x, self.y = x, y

class Velocity():
    def __init__(self, x=0.0, y=0.0):
        self.x, self.y = x, y

class Lifetime():
    def __init__(self, timer=1.0):
        self.timer = timer

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
        lifetime = Lifetime(random.random() * 10 + 5)
        eid = scene.new(position, lifetime)
        eids.append(eid)
    return scene, eids


@benchmark("mecs", "create", "0 components", setup=lambda hparams: Scene())
def mecs_create_entities(scene, hparams):
    for _ in range(hparams.count):
        scene.new()

@benchmark("mecs", "create", "1 component", setup=lambda hparams: Scene())
def mecs_create_entities_one_component(scene, hparams):
    for _ in range(hparams.count):
        scene.new(Position())

@benchmark("mecs", "create", "2 components", setup=lambda hparams: Scene())
def mecs_create_entities_two_components(scene, hparams):
    for _ in range(hparams.count):
        scene.new(Position(), Velocity())

@benchmark("mecs", "create", "3 components", setup=lambda hparams: Scene())
def mecs_create_entities_three_components(scene, hparams):
    for _ in range(hparams.count):
        scene.new(Position(), Velocity(), Lifetime())

@benchmark("mecs", "query", "all entities", setup=mecs_setup_full)
def mecs_query_all_entities(setup, hparams):
    scene, _ = setup
    for _ in scene.select():
        pass

@benchmark("mecs", "query", "1 component", setup=mecs_setup_mixed)
def mecs_query_one_component(setup, hparams):
    scene, _ = setup
    for _ in scene.select(Position):
        pass

@benchmark("mecs", "query", "2 components", setup=mecs_setup_mixed)
def mecs_query_two_components(setup, hparams):
    scene, _ = setup
    for _ in scene.select(Position, Velocity):
        pass

@benchmark("mecs", "query", "3 components", setup=mecs_setup_mixed)
def mecs_query_three_components(setup, hparams):
    scene, _ = setup
    for _ in scene.select(Position, Velocity, Lifetime):
        pass

@benchmark("mecs", "add", "1 component", setup=mecs_setup_empty)
def mecs_add_one_component(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.set(eid, Position())

@benchmark("mecs", "add", "2 components", setup=mecs_setup_empty)
def mecs_add_two_components(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.set(eid, Position(), Velocity())


@benchmark("mecs", "add", "3 components", setup=mecs_setup_empty)
def mecs_add_three_components(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.set(eid, Position(), Velocity(), Lifetime())

@benchmark("mecs", "replace", "1 component", setup=mecs_setup_full)
def mecs_overwrite_one_component(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.set(eid, Position())

@benchmark("mecs", "replace", "2 components", setup=mecs_setup_full)
def mecs_overwrite_two_components(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.set(eid, Position(), Velocity())


@benchmark("mecs", "replace", "3 components", setup=mecs_setup_full)
def mecs_overwrite_three_components(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.set(eid, Position(), Velocity(), Lifetime())

@benchmark("mecs", "has", "1 component", setup=mecs_setup_full)
def mecs_has_one_component(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.has(eid, Position)

@benchmark("mecs", "has", "2 components", setup=mecs_setup_full)
def mecs_has_two_components(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.has(eid, Position, Velocity)

@benchmark("mecs", "has", "3 components", setup=mecs_setup_full)
def mecs_has_three_components(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.has(eid, Position, Velocity, Lifetime)

@benchmark("mecs", "has", "3 components (false)", setup=mecs_setup_partial)
def mecs_has_three_components_false(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.has(eid, Position, Velocity, Lifetime)

@benchmark("mecs", "get", "1 component", setup=mecs_setup_full)
def mecs_get_one_component(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.get(eid, Position)

@benchmark("mecs", "get", "2 components", setup=mecs_setup_full)
def mecs_get_two_components(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.collect(eid, Position, Velocity)

@benchmark("mecs", "get", "3 components", setup=mecs_setup_full)
def mecs_get_three_components(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.collect(eid, Position, Velocity, Lifetime)

@benchmark("mecs", "remove", "1 component", setup=mecs_setup_full)
def mecs_remove_one_component(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.remove(eid, Position)

@benchmark("mecs", "remove", "2 components", setup=mecs_setup_full)
def mecs_remove_two_components(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.remove(eid, Position, Velocity)

@benchmark("mecs", "remove", "3 components", setup=mecs_setup_full)
def mecs_remove_three_components(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.remove(eid, Position, Velocity, Lifetime)

@benchmark("mecs", "destroy", "0 components", setup=mecs_setup_empty)
def mecs_destroy_zero_components(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.free(eid)

@benchmark("mecs", "destroy", "3 components", setup=mecs_setup_full)
def mecs_destroy_three_components(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.free(eid)

@benchmark("mecs", "archetype", "3 components", setup=mecs_setup_full)
def mecs_archetype_three_components(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.archetype(eid)

@benchmark("mecs", "components", "3 components", setup=mecs_setup_full)
def mecs_components_three_components(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.components(eid)

@benchmark("mecs", "example", "movement")
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
    for _ in range(hparams.count):
        position = Position(random.random() * 200 - 100, random.random() * 200 - 100)
        velocity = Velocity(random.random() * 200 - 100, random.random() * 200 - 100)
        lifetime = Lifetime(random.random() * 10 - 5)
        eid = world.create_entity(position, velocity, lifetime)
        eids.append(eid)

        position = Position(random.random() * 200 - 100, random.random() * 200 - 100)
        lifetime = Lifetime(random.random() * 10 - 5)
        eid = world.create_entity(position, lifetime)
        eids.append(eid)
    return world, eids


@benchmark("esper", "create", "0 components", setup=lambda hparams: (esper.World(), []))
def esper_create_zero_components(setup, hparams):
    world, _ = setup
    for _ in range(hparams.count):
        world.create_entity()

@benchmark("esper", "create", "1 component", setup=lambda hparams: (esper.World(), []))
def esper_create_one_component(setup, hparams):
    world, _ = setup
    for _ in range(hparams.count):
        world.create_entity(Position())

@benchmark("esper", "create", "2 components", setup=lambda hparams: (esper.World(), []))
def esper_create_two_components(setup, hparams):
    world, _ = setup
    for _ in range(hparams.count):
        world.create_entity(Position(), Velocity())

@benchmark("esper", "create", "3 components", setup=lambda hparams: (esper.World(), []))
def esper_create_three_components(setup, hparams):
    world, _ = setup
    for _ in range(hparams.count):
        world.create_entity(Position(), Velocity(), Lifetime())

@benchmark("esper", "query", "1 component", setup=esper_setup_mixed)
def esper_query_one_component(setup, hparams):
    world, _ = setup
    for _, _ in world.get_component(Position):
        pass

@benchmark("esper", "query", "2 components", setup=esper_setup_mixed)
def esper_query_two_components(setup, hparams):
    world, _ = setup
    for _, _ in world.get_components(Position, Velocity):
        pass

@benchmark("esper", "query", "3 components", setup=esper_setup_mixed)
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
            help="The number of entities to benchmark (default 10**5)")
    hparams = parser.parse_args()

    functions = [
        mecs_create_entities,
        mecs_create_entities_one_component,
        mecs_create_entities_two_components,
        mecs_create_entities_three_components,
        mecs_query_all_entities,
        mecs_query_one_component,
        mecs_query_two_components,
        mecs_query_three_components,
        mecs_add_one_component,
        mecs_add_two_components,
        mecs_add_three_components,
        mecs_overwrite_one_component,
        mecs_overwrite_two_components,
        mecs_overwrite_three_components,
        mecs_has_one_component,
        mecs_has_two_components,
        mecs_has_three_components,
        mecs_has_three_components_false,
        mecs_get_one_component,
        mecs_get_two_components,
        mecs_get_three_components,
        mecs_remove_one_component,
        mecs_remove_two_components,
        mecs_remove_three_components,
        mecs_destroy_zero_components,
        mecs_destroy_three_components,
        mecs_archetype_three_components,
        mecs_components_three_components,
        mecs_example_movement,

        esper_create_zero_components,
        esper_create_one_component,
        esper_create_two_components,
        esper_create_three_components,
        esper_query_one_component,
        esper_query_two_components,
        esper_query_three_components
    ]

    if hparams.backend is not None:
        backends = hparams.backend.split(",")
    if hparams.task is not None:
        tasks = hparams.task.split(",")

    for f in functions:
        if (hparams.backend is None or f.backend in backends) and (hparams.task is None or f.task in tasks):
            f(hparams, verbose=True)

if __name__ == "__main__":
    main()
