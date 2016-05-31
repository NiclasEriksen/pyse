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
            if p.body:
                x, y = p.body.position()
                x, y = x + world.offset_x, y + world.offset_y
                s.sprite.x, s.sprite.y = x, y


class ParallaxSystem(System):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (SpriteObject, ParallaxObject)

    def process(self, world, componentsets):
        for s, p in componentsets:
            s.sprite.x = int(-world.width + world.offset_x // p.ratio)


class SpriteBatchSystem(System):
    def __init__(self, world):
        self.is_applicator = True
        self.componenttypes = (SpriteObject, )

    def process(self, world, componentsets):
        for s, *rest in componentsets:
            if s.batch and not s.sprite.batch:
                try:
                    s.sprite.batch = world.batches[s.batch]
                except KeyError:
                    print("NO SUCH BATCH: {0}".format(s.batch))


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
