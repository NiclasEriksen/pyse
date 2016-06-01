import os
import logging
import pyglet
from utils.ebs import World
from pyglet.gl import *
import pymunk
from functions import *
from collections import OrderedDict
from tile import tile_img
import entities
import components
import systems
from player import Player
from editor import Editor

pyglet.options['debug_gl'] = False
pyglet.options["audio"] = ("openal", "silent")

# Logging
logging.basicConfig(
    filename='debug.log',
    filemode='w',
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)
logger.setLevel(logging.DEBUG)

# GLOBAL VARIABLES
ROOT = os.path.dirname(__file__)
RES_PATH = os.path.join(ROOT, "resources")
PAUSED = False
FPS = 60.0               # Target frames per second
SCALING = 4
RES_X, RES_Y = 1280, 720
MAP_WIDTH = 1500
# print(RES_X / 8, RES_Y / 8)
# print(RES_X % 8, RES_Y % 8)

# Bullshit platformer globals
PLAYER_VELOCITY = 100.
PLAYER_GROUND_ACCEL_TIME = 0.05
PLAYER_GROUND_ACCEL = PLAYER_VELOCITY / PLAYER_GROUND_ACCEL_TIME

PLAYER_AIR_ACCEL_TIME = 0.25
PLAYER_AIR_ACCEL = PLAYER_VELOCITY / PLAYER_AIR_ACCEL_TIME

JUMP_HEIGHT = (16.) * 2
JUMP_BOOST_HEIGHT = (24.)
JUMP_CUTOFF_VELOCITY = 100
FALL_VELOCITY = 350.

JUMP_LENIENCY = 0.05

HEAD_FRICTION = 0.7

PLATFORM_SPEED = 1

# Get information about the OS and display #
platform = pyglet.window.get_platform()
display = platform.get_default_display()
screen = display.get_default_screen()

# Limit the frames per second #
pyglet.clock.set_fps_limit(FPS)


class CollideableObject:

    def __init__(self, game, x, y, w, h):
        self.game = game
        self.x, self.y, self.width, self.height = (
            int(x - w / 2),
            int(y - h / 2),
            w, h
        )
        self.sprite = pyglet.sprite.Sprite(
            self.game.textures["block"],
            x=self.x, y=self.y,
            batch=self.game.batches["objects"], subpixel=False
        )

        box_points = self.game.shapes.rect(w, h, x=self.x, y=self.y)
        self.shape = pymunk.Poly(
            self.game.phys_space.static_body, box_points
        )
        # self.shape.collision_type = 1
        self.shape.friction = 1.
        self.shape.elasticity = 0
        self.shape.group = 1
        self.game.phys_space.add(self.shape)

    def update(self):
        ox = self.game.offset_x
        self.sprite.x = int(self.x + ox)


class ShapeGenerator:

    def rect(self, w, h, x=0, y=0):
        return [(x, y), (x, y + h), (x + w, y + h), (x + w, y)]

    def trapese(self, bw, tw, h, x=0, y=0):
        w = max(bw, tw)
        return [
            (x + (w - tw) // 2, y + h),
            (x + w - ((w - tw) // 2), y + h),
            (x + w - ((w - bw) // 2), y),
            (x + (w - bw) // 2, y)
        ]


class GameWorld(World):

    def __init__(self):
        self.window = GameWindow(self)
        # self.window.on_mouse_motion = self.on_mouse_motion
        self.window.on_mouse_press = self.on_mouse_press
        # self.window.on_mouse_scroll = self.on_mouse_scroll
        self.window.on_key_press = self.on_key_press
        self.window.on_key_release = self.on_key_release
        # self.window.on_resize = self.on_resize
        if (
            not self.window.width % SCALING and
            not self.window.height % SCALING
        ):
            self.width = self.window.width // SCALING
            self.height = self.window.height // SCALING
            logger.info(
                "Render resolution set to {0}x{1}.".format(
                    self.width, self.height
                )
            )
        else:
            self.width = (
                (self.window.width - self.window.width % SCALING) // SCALING
            )
            self.height = (
                (self.window.height - self.window.height % SCALING) // SCALING
            )
            logger.info(
                "Resolution doesn't scale nicely, resized to {0}x{1}.".format(
                    self.width, self.height
                )
            )
        self.offset_x, self.offset_y = 0, 0
        self.map_width = MAP_WIDTH

        logger.info("Loading textures...")
        self.load_textures()
        logger.info("Loading sounds...")
        self.load_sounds()

        logger.debug("Defining graphics batches.")
        self.batches = OrderedDict()
        self.batches["bg"] = pyglet.graphics.Batch()
        self.batches["objects"] = pyglet.graphics.Batch()
        self.batches["player"] = pyglet.graphics.Batch()
        self.batches["fg"] = pyglet.graphics.Batch()

        logger.info("Initializing media player.")
        self.media_player = pyglet.media.Player()
        self.sfx_player = pyglet.media.Player()
        self.sfx_player.eos_action = self.sfx_player.EOS_STOP
        self.bgm_looper = pyglet.media.SourceGroup(
            self.sounds["bgm01"].audio_format, None
        )
        self.bgm_looper.loop = True
        logger.debug("Queuing background music...")
        self.bgm_looper.queue(self.sounds["bgm01"])
        self.media_player.queue(self.bgm_looper)
        self.media_player.play()    # Playing and pausing the media player
        self.media_player.pause()   # in order to avoid delay on sfx play

        logger.debug("Loading game editor.")
        self.editor = Editor(self)
        self.shapes = ShapeGenerator()

        logger.info("Creating physics space.")
        self.phys_space = pymunk.Space()
        self.phys_space.add_collision_handler(
            1, 1, post_solve=self.collision_handler
        )
        # self.phys_space.damping = 0.0001
        self.phys_space.gravity = 0, -1000

        logger.debug("Loading background and foreground sprites.")
        self.ground_sprite = pyglet.sprite.Sprite(
            self.textures["ground"],
            x=0, y=0,
            batch=self.batches["objects"], subpixel=False
        )

        super().__init__()
        logger.info("Spawning static game objects.")

        for i in range(self.width // 4, self.width - self.width // 4, 16):
                entities.Block(self, x=i, y=self.height - 64, w=16, h=16)
        for i in range(self.width // 4, self.width - self.width // 4, 16):
                entities.Block(self, x=i, y=32, w=16, h=16)

        static_lines = [
            pymunk.Segment(
                self.phys_space.static_body, (0, 15), (self.map_width, 15), 1
            ),
            pymunk.Segment(
                self.phys_space.static_body, (0, 0), (0, self.height), 1
            ),
            pymunk.Segment(
                self.phys_space.static_body,
                (self.map_width, 0),
                (self.map_width, self.height), 1
            ),
            pymunk.Segment(
                self.phys_space.static_body,
                (0, self.height),
                (self.map_width, self.height), 1
            ),
            # pymunk.Segment(
            #     self.phys_space.static_body, (100, 400), (400, 600), 5
            # )
        ]
        for line in static_lines:
            line.collision_type = 1
            line.elasticity = 0
            line.friction = 1
            line.group = 1

        self.phys_space.add(static_lines)

        logger.info("Spawning player.")
        self.player = Player(self)
        self.timer_enabled = False
        self.start_systems()
        self.bg_test = entities.BackgroundImage(self)

    def spawn_player(self):
        pass

    def start_systems(self):
        self.add_system(systems.SpritePosSystem(self))
        self.add_system(systems.StaticSpritePosSystem(self))
        self.add_system(systems.ParallaxSystem(self))
        self.add_system(systems.SpriteBatchSystem(self))
        self.add_system(systems.RenderSystem(self))

    def play_sound(self, name):
        s = self.sounds[name]
        s.play()

    def collision_handler(self, space, arbiter):
        if arbiter.is_first_contact:
            self.play_sound("dunk")
        return False

    def add_block(self, x, y, w=16, h=16):
        entities.Block(self, x=x, y=y, w=w, h=h)

    def remove_block(self, x, y):
        blocks = self.get_components(components.StaticPhysicsBody)
        for b in reversed(blocks):
            if b.shape.point_query((x, y)):
                self.phys_space.remove(b.shape)
                e = self.get_entities(b)
                self.delete_entities(e)
                break

    def get_texture(self, name):
        try:
            return self.textures[name]
        except KeyError:
            logger.debug(
                "No texture with identifier '{0}',\
                 returning debug texture".format(
                    name
                )
            )
            return self.textures["debug"]

    def load_textures(self):
        debug_img = pyglet.resource.image("resources/debug.png")
        player_img_l = (
            pyglet.resource.image('resources/dumb.png')
        )
        player_img_r = (
            pyglet.resource.image('resources/dumb_r.png')
        )
        block_img = (
            pyglet.resource.image('resources/block.png')
        )

        ground_img = pyglet.image.ImageData(
            self.map_width - (self.map_width % 16), 16, 'RGB', tile_img(
                "resources/ground_grass.png",
                self.map_width - (self.map_width % 16), 16
            ), pitch=(self.map_width - (self.map_width % 16)) * 3
        ).get_texture()
        bg_img = pyglet.image.ImageData(
            self.map_width + self.width, self.height, 'RGB', tile_img(
                "resources/bg.png",
                self.map_width + self.width, self.height
            ), pitch=(self.map_width + self.width) * 3
        ).get_texture()

        self.textures = dict(
            debug=debug_img,
            player_l=player_img_l,
            player_r=player_img_r,
            block=block_img,
            bg=bg_img,
            ground=ground_img
        )

    def load_sounds(self):
        jump1 = pyglet.resource.media("jump1.ogg", streaming=False)
        jump2 = pyglet.resource.media("jump2.ogg", streaming=False)
        jump3 = pyglet.resource.media("jump3.ogg", streaming=False)
        dunk = pyglet.resource.media("dunk.ogg", streaming=False)
        bgm01 = pyglet.resource.media("bgm01.ogg")

        self.sounds = dict(
            jump1=jump1,
            jump2=jump2,
            jump3=jump3,
            dunk=dunk,
            bgm01=bgm01
        )

    def on_key_press(self, button, modifiers):
        k = pyglet.window.key
        d = self.player.direction
        if button == k.SPACE:
            d["up"] = True
        elif button == k.ESCAPE:
            pyglet.app.exit()
        if button == k.A or button == k.LEFT:
            d["left"] = True
        if button == k.D or button == k.RIGHT:
            d["right"] = True
        if button == k.P:
            if self.media_player.playing:
                self.media_player.pause()
            else:
                self.media_player.play()
        if button == k.PLUS:
            self.offset_x += 10
        if button == k.MINUS:
            self.offset_x -= 10
        self.player.direction = d

    def on_mouse_press(self, x, y, btn, mod):
        # print(x, y, btn)
        if btn == 1:
            self.add_block(
                x // SCALING - self.offset_x, y // SCALING
            )
        elif btn == 4:
            self.remove_block(
                x // SCALING - self.offset_x, y // SCALING
            )

    def on_key_release(self, button, modifiers):
        k = pyglet.window.key
        d = self.player.direction
        if button == k.SPACE:
            d["up"] = False
        if button == k.A or button == k.LEFT:
            d["left"] = False
        if button == k.D or button == k.RIGHT:
            d["right"] = False

    def update(self, dt):
        self.player.update(dt)
        self.offset_x = self.width / 2 - self.player.phys_body.position[0]
        self.ground_sprite.x = int(self.offset_x)
        self.editor.update(dt)
        for i in range(30):
            self.phys_space.step(dt / 30)

    def get_pixel_aligned_pos(self, x, y):
        return int(x - (x % SCALING)), int(y - (y % SCALING))

    def render(self, dt):
        glClearColor(0.2, 0.2, 0.2, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        for k, v in self.batches.items():
            glEnable(GL_TEXTURE_2D)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            v.draw()


class GameWindow(pyglet.window.Window):  # Main game window

    def __init__(self, game):
        # Template for multisampling
        self.game = game
        logger.debug("Setting gl configuration.")
        gl_template = pyglet.gl.Config(
            sample_buffers=1,
            samples=2,
            alpha_size=8,
            stencil_size=8
        )
        try:  # to enable multisampling
            logger.debug("Multisampling enabled.")
            gl_config = screen.get_best_config(gl_template)
        except pyglet.window.NoSuchConfigException:
            logger.warning("Failed to enable multisampling.")
            gl_template = pyglet.gl.Config(alpha_size=8)
            gl_config = screen.get_best_config(gl_template)
        gl_context = gl_config.create_context(None)
        logger.info("Initializing main window.")
        super(GameWindow, self).__init__(
            context=gl_context,
            config=gl_config,
            resizable=False,
            vsync=True,
        )
        if not self.fullscreen:
            self.set_location(
                (screen.width - RES_X) // 2,
                (screen.height - RES_Y) // 2
            )
            self.width, self.height = RES_X, RES_Y

        logger.debug("Setting GL flags for pixel scaling.")
        glScalef(4.0, 4.0, 4.0)
        # These have seemingly no effects and are just attempts at fixing
        # the blurry texture that happens at random
        glEnable(GL_TEXTURE_2D)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)


if __name__ == "__main__":
    # Initialize world
    g = GameWorld()

    # Schedule the update function on the world to run every frame.
    pyglet.clock.schedule_interval(g.update, 1.0 / FPS)
    # pyglet.clock.schedule_interval(g.render, 1.0 / FPS)
    pyglet.clock.schedule_interval(g.process, 1.0 / FPS)

    # Initialize pyglet app
    pyglet.app.run()
