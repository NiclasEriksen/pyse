from utils.ebs import Entity
from pymunk import Poly, Circle, Body, inf
from components import *


class Player(Entity):

    def __init__(self, world, x=0, y=0):
        self.movable = Movable()
        self.spriteobject = SpriteObject(
            world.get_texture("player"), x, y
        )
        sw = self.spriteobject.sprite.width
        ratio = 16 / sw
        self.spriteobject.sprite.scale = ratio
        phys_body = Body(5, inf)
        phys_body.position = x, y
        shape = Circle(phys_body, 8, (8, 8))
        self.physicsbody = PhysicsBody(shape)
        world.phys_space.add(self.physicsbody.body, self.physicsbody.shape)
        self.groundingobject = GroundingObject()


class StaticEntity(Entity):

    def __init__(self, world, shape, x=0, y=0):
        self.staticphysicsbody = StaticPhysicsBody(shape, x, y)
        world.phys_space.add(self.staticphysicsbody.shape)


class Platform(StaticEntity):

    def __init__(self, world):
        shape = None
        super().__init__(world, shape)
        self.spriteobject = SpriteObject(
            world.get_texture("debug"), 0, 0
        )


class Block(StaticEntity):

    def __init__(self, world, x=0, y=0, w=16, h=16):
        x, y = int(x), int(y)
        shape = Poly(
            world.phys_space.static_body, world.shapes.rect(w, h, x=x, y=y)
        )
        super().__init__(world, shape, x=x, y=y)
        self.spriteobject = SpriteObject(
            world.get_texture("block"), x, y, batch="objects"
        )
        sw = self.spriteobject.sprite.width
        ratio = w / sw
        self.spriteobject.sprite.scale = ratio


class GroundBlock(StaticEntity):

    def __init__(self, world, x=0, y=0, w=16, h=16):
        x, y = int(x), int(y)
        shape = Poly(
            world.phys_space.static_body, world.shapes.rect(w, h, x=x, y=y)
        )
        super().__init__(world, shape, x=x, y=y)
        self.spriteobject = SpriteObject(
            world.get_texture("ground"), x, y, batch="objects"
        )


class Orb(StaticEntity):

    def __init__(self, world, x=0, y=0, r=8):
        x, y = int(x), int(y)
        shape = Circle(
            world.phys_space.static_body, r, (x + r, y + r)
        )
        super().__init__(world, shape, x=x, y=y)
        self.spriteobject = SpriteObject(
            world.get_texture("orb"), x, y, batch="objects"
        )
        sw = self.spriteobject.sprite.width
        ratio = (r * 2) / sw
        self.spriteobject.sprite.scale = ratio


class BackgroundImage(Entity):
    def __init__(self, world):
        self.spriteobject = SpriteObject(
            world.get_texture("bg"),
            0, 0, batch="bg"
        )
        self.parallaxobject = ParallaxObject()
