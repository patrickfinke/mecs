from mecs import Scene
import time, random

class Position():
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __repr__(self):
        return f"<Position({self.x}, {self.y})>"

class Velocity():
    def __init__(self, vx, vy):
        self.vx, self.vy = vx, vy

    def __repr__(self):
        return f"<Velocity({self.vx}, {self.vy})>"

class MovementSystem():
    def update(self, scene, dt=1, **kwargs):
        for eid, (pos, vel) in scene.filter(Position, Velocity):
            pos.x += vel.vx * dt
            pos.y += vel.vy * dt

class ReportSystem():
    def update(self, scene, dt=1, **kwargs):
        for eid, (pos, vel) in scene.filter(Position, Velocity):
            print(eid, pos, vel)
        print()

def main():
    scene = Scene()
    systems = [MovementSystem(), ReportSystem()]

    values = list(range(1, 11))
    for _ in range(10):
        eid = scene.new()
        scene.add(eid, Position(random.choice(values), random.choice(values)))
        scene.add(eid, Velocity(random.choice(values), random.choice(values)))

    print("[press Ctrl+C to stop]")
    try:
        while True:
            scene.update(*systems, dt=1)
            time.sleep(1)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
