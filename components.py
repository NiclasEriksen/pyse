import pyglet.sprite
import pymunk.vec2d


class Movable(object):

    def __init__(self):
        self.active = True
        self.direction = "right"


class JumpObject(object):

    def __init__(self):
        self.cd = 0.3
        self.cd_timer = 0.


class InputObject(object):

    def __init__(self, input_type):
        self.input_type = input_type


class DirectionalSprite(object):

    def __init__(self, world, name):
        gt = world.get_texture
        self.textures = dict(
            left=gt("{0}_l".format(name)),
            right=gt("{0}_r".format(name)),
            up=gt("{0}_u".format(name)),
            error=gt("debug")
        )

    def get(self, direction):
        try:
            return self.textures[direction]
        except KeyError:
            return self.textures["error"]


class SpriteObject(object):

    def __init__(self, img, x, y, w=None, h=None, batch=None):
        self.sprite = pyglet.sprite.Sprite(
            img, x, y, subpixel=False
        )
        hratio = 1
        if w:
            sw = self.sprite.width
            hratio = w / sw
        vratio = 1
        if h:
            sh = self.sprite.height
            vratio = h / sh
        self.sprite.scale = min(vratio, hratio)
        self.batch = batch


class ButtonIcon(object):

    def __init__(self, img, x, y, w=None, h=None, batch=None):
        self.sprite = pyglet.sprite.Sprite(
            img, x, y, batch=batch, subpixel=False
        )
        hratio = 1
        if w:
            sw = self.sprite.width
            hratio = w / sw
        vratio = 1
        if h:
            sh = self.sprite.height
            vratio = h / sh
        self.sprite.scale = min(vratio, hratio)


class FloatingSprite(object):

    def __init__(self, x, y):
        self.x, self.y = x, y


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

    def __init__(self, action, params):
        self.action = action
        self.params = params

    def get(self):
        if self.params:
            # print("Calling with params {0}".format(self.params))
            self.action(self.params)
        else:
            # print("Calling without params")
            self.action()


class MouseControlled(object):
    def __init__(self, area, action=None, btn="left"):
        self.area = area
        self.action = action
        self.btn = btn


class MouseScreenControlled(object):
    def __init__(self, action=None, params=None, btn="left"):
        self.action = action
        self.params = params
        self.btn = btn


class MouseListen(object):
    def __init__(self, btn=None, event_type="click"):
        self.btn = btn
        self.event_type = event_type


class KeyboardListen(object):
    def __init__(self, btn=None):
        self.btn = btn


class KeyboardControlled(object):
    def __init__(self, action=None, params=None, btn=None):
        self.action = action
        self.params = params
        self.btn = btn


class MouseClicked(object):
    def __init__(self, x, y, btn):
        self.x, self.y, self.btn = x, y, btn
        self.handled = False


class KeyPressed(object):
    def __init__(self, btn):
        self.btn = btn
        self.handled = False


class MouseBoundObject(object):
    def __init__(self, offset=(0, 0)):
        self.offset = offset


class SFXObject(object):

    def __init__(self, sound):
        self.sound = sound


class SoundEmitter(object):

    def __init__(self):
        self.sound = None
