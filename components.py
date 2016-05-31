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

    def __init__(self):
        self.body = None


class ActionBinding(object):
    """
        Binds input/event signals to functions.
    """

    def __init__(self):
        pass


class SoundEmitter(object):

    def __init__(self):
        self.sound = None
