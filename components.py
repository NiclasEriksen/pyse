import pyglet.sprite
import pymunk.vec2d


class Movable(object):

    def __init__(self):
        self.active = True


class SpriteObject(object):

    def __init__(self, img, x, y, batch=None):
        self.sprite = pyglet.sprite.Sprite(
            img, x, y, subpixel=False
        )
        self.batch = batch


class ParallaxObject(object):
    def __init__(self, ratio=2):
        self.ratio = ratio


class PhysicsBody(object):

    def __init__(self, shape):
        self.active = False
        self.shape = shape
        self.body = shape.body
        # self.shape.collision_type = 1
        self.shape.friction = 1.
        self.shape.elasticity = 0
        self.shape.group = 0


class GroundingObject(object):

    def __init__(self):
        self.grounding = {
            'normal': pymunk.vec2d.Vec2d.zero(),
            'penetration': pymunk.vec2d.Vec2d.zero(),
            'impulse': pymunk.vec2d.Vec2d.zero(),
            'position': pymunk.vec2d.Vec2d.zero(),
            'body': None
        }
        self.well_grounded = False


class StaticPhysicsBody(object):

    def __init__(self, shape, x, y):
        self.x, self.y = x, y
        self.shape = shape
        # self.shape.collision_type = 1
        self.shape.friction = 1.
        self.shape.elasticity = 0
        self.shape.group = 1


class ActionBinding(object):
    """
        Binds input/event signals to functions.
    """

    def __init__(self):
        pass


class SFXObject(object):

    def __init__(self, sound):
        self.sound = sound


class SoundEmitter(object):

    def __init__(self):
        self.sound = None
