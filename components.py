import pyglet.sprite


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
        # self.shape.collision_type = 1
        self.shape.friction = 1.
        self.shape.elasticity = 0
        self.shape.group = 1


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


class SoundEmitter(object):

    def __init__(self):
        self.sound = None
