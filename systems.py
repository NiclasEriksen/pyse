from utils.ebs import System
from pyglet.gl import *
from entities import *
from components import *


class SpritePosSystem(System):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (SpriteObject, PhysicsBody)

    def process(self, world, componentsets):
        # print(*componentsets)
        for s, p, *rest in componentsets:
            if p.shape:
                x, y = p.shape.body.position
                x, y = x + world.offset_x, y + world.offset_y
                s.sprite.x, s.sprite.y = x, y


class FloatingSpritePosSystem(System):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (SpriteObject, FloatingSprite)

    def process(self, world, componentsets):
        for s, f in componentsets:
            x, y = f.x + world.offset_x, f.y + world.offset_y
            s.sprite.x, s.sprite.y = int(x), int(y)


class StaticSpritePosSystem(System):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (SpriteObject, StaticPhysicsBody)

    def process(self, world, componentsets):
        # print(*componentsets)
        for s, p, *rest in componentsets:
            if p.shape:
                x, y = p.x, p.y
                x, y = x + world.offset_x, y + world.offset_y
                s.sprite.x, s.sprite.y = int(x), int(y)


class DirectionalSpriteSystem(System):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (SpriteObject, DirectionalSprite, Movable)

    def process(self, world, componentsets):
        for so, do, m in componentsets:
            so.sprite.image = do.get(m.direction)


class ParallaxSystem(System):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (SpriteObject, ParallaxObject)

    def process(self, world, componentsets):
        for s, p in componentsets:
            s.sprite.x = int(-world.width + world.offset_x // p.ratio)


class SpriteBatchSystem(System):
    def __init__(self, world):
        self.is_applicator = False
        self.componenttypes = (SpriteObject, )

    def process(self, world, componentsets):
        for s in componentsets:
            if s.batch and not s.sprite.batch:
                try:
                    s.sprite.batch = world.batches[s.batch]
                    world.log.debug(
                        "Added {0} sprite to batch '{1}'".format(
                            s, s.batch
                        )
                    )
                except KeyError:
                    world.log.error("NO SUCH BATCH: {0}".format(s.batch))
                    s.batch = None


class SoundEffectSystem(System):
    def __init__(self, world):
        self.is_applicator = False
        self.componenttypes = (SFXObject, )

    def process(self, world, componentsets):
        for sfx, *rest in componentsets:
            world.log.info(sfx)


class GameOffsetSystem(System):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (None, )

    def process(self, world, componentsets):
        pass


class MousePressAreaSystem(System):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (MouseControlled, MouseListen)

    def process(self, world, componentsets):
        if world.mouse_click:
            click = world.mouse_click
            if not click.handled:
                for mc, ml in componentsets:
                    if ml.btn == click.btn:
                        if (
                            click.x >= mc.area[0][0] and
                            click.x <= mc.area[1][0] and
                            click.y >= mc.area[0][1] and
                            click.y <= mc.area[1][1]
                        ):
                            world.log.debug("Button hit!")
                            mc.action.get()
                            world.mouse_click.handled = True
                            break


class MousePressSystem(System):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (MouseListen, MouseScreenControlled)

    def process(self, world, componentsets):
        if world.mouse_click:
            c = world.mouse_click
            for ml, msc in componentsets:
                if not c.handled:
                    if ml.btn == c.btn:
                        world.log.debug("Calling on mouse press action.")
                        msc.action()
                        world.mouse_click.handled = True


class InputMovementSystem(System):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (Movable, PhysicsBody, InputObject)

    def process(self, world, componentsets):
        for m, pb, i in componentsets:
            pass


class RenderSystem(System):
    def __init__(self, world):
        self.is_applicator = False
        self.componenttypes = (SpriteObject, )

    def draw_batchless(self, sprite):
        sprite.draw()

    def process(self, world, componentsets):
        glClearColor(0.2, 0.2, 0.2, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        for k, v in world.batches.items():
            glEnable(GL_TEXTURE_2D)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            v.draw()

        for s in componentsets:
            if not s.sprite.batch and not s.batch:
                self.draw_batchless(s.sprite)
