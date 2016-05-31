

class Movable(object):

    def __init__(self):
        self.active = True


class SpriteObject(object):

    def __init__(self, img, x, y):
        self.sprite = None


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
