from utils.ebs import System
from entities import *
from components import *


class MoveSystem(System):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (Position, Velocity)

    def process(self, world, componentsets):
        # print(*componentsets)
        for pos, vel, *rest in componentsets:
            pos.set(
                pos.x + vel.x * world.dt,
                pos.y + vel.y * world.dt
            )
