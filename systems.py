from utils.ebs import System
from entities import *
from components import *


class SpritePosSystem(System):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (SpriteObject, PhysicsBody)

    def process(self, world, componentsets):
        # print(*componentsets)
        for s, p, *rest in componentsets:
            if p.body:
                x, y = p.body.position()
                x, y = x + world.offset_x, y + world.offset_y
                s.sprite.x, s.sprite.y = x, y
