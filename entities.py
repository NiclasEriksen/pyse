from utils.ebs import Entity
from components import *


class Player(Entity):

    def __init__(self, world):
        pass


class StaticEntity(Entity):

    def __init__(self, world):
        pass


class Platform(StaticEntity):

    def __init__(self, world):
        super().__init__(world)
        self.physicsbody = PhysicsBody()
        self.spriteobject = SpriteObject(
            world.get_texture("debug"), 0, 0
        )


class BackgroundImage(Entity):
    def __init__(self, world):
        self.spriteobject = SpriteObject(
            world.get_texture("bg"),
            0, 0, batch="bg"
        )
        self.parallaxobject = ParallaxObject()
