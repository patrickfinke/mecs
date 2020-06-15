import sys, time, argparse, random
from mecs import Scene, CommandBuffer

def mean(values):
    """Calculate the mean value."""

    return sum(values) / len(values)

def benchmark(name, restarts=10, metric=mean, ndigits=4, setup=None):
    """Benchmark a function."""

    def timer(function):
        def wrapper(hparams, verbose=True):
            times = []
            for _ in range(restarts):
                setup_result = setup(hparams) if setup is not None else Scene()

                start = time.time()
                function(setup_result, hparams)
                end = time.time()
                times.append(end - start)
                
            result = metric(times)
            if verbose:
                print(f"{name}: {round(result, ndigits)} seconds")
            return result
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

@benchmark("mecs/create entities/0 components", setup=lambda hparams: Scene())
def mecs_create_entities(scene, hparams):
    for _ in range(hparams.count):
        scene.new()

@benchmark("mecs/create entities/1 component", setup=lambda hparams: Scene())
def mecs_create_entities_one_component(scene, hparams):
    for _ in range(hparams.count):
        scene.new(Position())

@benchmark("mecs/create entities/2 components", setup=lambda hparams: Scene())
def mecs_create_entities_two_components(scene, hparams):
    for _ in range(hparams.count):
        scene.new(Position(), Velocity())

@benchmark("mecs/create entities/3 components", setup=lambda hparams: Scene())
def mecs_create_entities_three_components(scene, hparams):
    for _ in range(hparams.count):
        scene.new(Position(), Velocity(), Lifetime())

@benchmark("mecs/query/all entities", setup=mecs_setup_full)
def mecs_query_all_entities(setup, hparams):
    scene, _ = setup
    for _ in scene.select():
        pass

@benchmark("mecs/query/1 component", setup=mecs_setup_full)
def mecs_query_one_component(setup, hparams):
    scene, _ = setup
    for _ in scene.select(Position):
        pass

@benchmark("mecs/query/2 components", setup=mecs_setup_full)
def mecs_query_two_components(setup, hparams):
    scene, _ = setup
    for _ in scene.select(Position, Velocity):
        pass

@benchmark("mecs/query/3 components", setup=mecs_setup_full)
def mecs_query_three_components(setup, hparams):
    scene, _ = setup
    for _ in scene.select(Position, Velocity, Lifetime):
        pass

@benchmark("mecs/add/1 component", setup=mecs_setup_empty)
def mecs_add_one_component(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.set(eid, Position())

@benchmark("mecs/add/2 components", setup=mecs_setup_empty)
def mecs_add_two_components(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.set(eid, Position(), Velocity())


@benchmark("mecs/add/3 components", setup=mecs_setup_empty)
def mecs_add_three_components(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.set(eid, Position(), Velocity(), Lifetime())

@benchmark("mecs/overwrite/1 component", setup=mecs_setup_full)
def mecs_overwrite_one_component(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.set(eid, Position())

@benchmark("mecs/overwrite/2 components", setup=mecs_setup_full)
def mecs_overwrite_two_components(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.set(eid, Position(), Velocity())


@benchmark("mecs/overwrite/3 components", setup=mecs_setup_full)
def mecs_overwrite_three_components(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.set(eid, Position(), Velocity(), Lifetime())

@benchmark("mecs/has/1 component", setup=mecs_setup_full)
def mecs_has_one_component(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.has(eid, Position)

@benchmark("mecs/has/2 components", setup=mecs_setup_full)
def mecs_has_two_components(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.has(eid, Position, Velocity)

@benchmark("mecs/has/3 components", setup=mecs_setup_full)
def mecs_has_three_components(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.has(eid, Position, Velocity, Lifetime)

@benchmark("mecs/has/3 components (false)", setup=mecs_setup_partial)
def mecs_has_three_components_false(setup, hparams):
    scene, eids = setup
    for eid in eids:
        scene.has(eid, Position, Velocity, Lifetime)

def main():
    parser = argparse.ArgumentParser()
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
        mecs_has_three_components_false
    ]

    for f in functions:
        f(hparams)

if __name__ == "__main__":
    main()
