import os
import logging
from collections import OrderedDict
import pyglet
from pyglet.gl import *
import pymunk
from utils.ebs import World
from functions import *
from load_config import ConfigSectionMap as load_cfg
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
SFX_PATH = os.path.join(RES_PATH, "audio")
TEX_PATH = os.path.join(RES_PATH, "textures")
FPS = 60.0               # Target frames per second

# Bullshit platformer globals
PLAYER_VELOCITY = 100.
PLAYER_GROUND_ACCEL_TIME = 0.05
PLAYER_GROUND_ACCEL = PLAYER_VELOCITY / PLAYER_GROUND_ACCEL_TIME

PLAYER_AIR_ACCEL_TIME = 0.25
PLAYER_AIR_ACCEL = PLAYER_VELOCITY / PLAYER_AIR_ACCEL_TIME

JUMP_HEIGHT = (24.) * 2
JUMP_BOOST_HEIGHT = (42.)
JUMP_CUTOFF_VELOCITY = 150
FALL_VELOCITY = 350.

JUMP_LENIENCY = 0.05

HEAD_FRICTION = 0.7

PLATFORM_SPEED = 1

# Get information about the OS and display #
platform = pyglet.window.get_platform()
display = platform.get_default_display()
screen = display.get_default_screen()


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
        super().__init__()
        self.log = logger
        self.cfg = load_cfg("Game")
        self.log.debug("Registering ebs systems.")
        self.start_systems()
        self.window = GameWindow(self)
        self.window.on_mouse_motion = self.on_mouse_motion
        self.window.on_mouse_press = self.on_mouse_press
        # self.window.on_mouse_scroll = self.on_mouse_scroll
        self.window.on_key_press = self.on_key_press
        self.window.on_key_release = self.on_key_release
        self.mouse_click = None
        # self.window.on_resize = self.on_resize
        s = load_cfg("Window")["scale"]
        self.scale = s
        if (
            not self.window.width % s and
            not self.window.height % s
        ):
            self.width = self.window.width // s
            self.height = self.window.height // s
            self.log.info(
                "Render resolution set to {0}x{1}.".format(
                    self.width, self.height
                )
            )
        else:
            self.width = (
                (self.window.width - self.window.width % s) // s
            )
            self.height = (
                (self.window.height - self.window.height % s) // s
            )
            self.log.info(
                "Resolution doesn't scale nicely, resized to {0}x{1}.".format(
                    self.width, self.height
                )
            )
        self.offset_x, self.offset_y = 0, 0
        self.map_width = self.cfg["map_width"]
        self.map_height = self.cfg["map_height"]

        self.log.info("Loading textures...")
        self.load_textures()
        self.log.info("Loading sounds...")
        self.load_sounds()

        self.log.debug("Defining graphics batches.")
        self.batches = OrderedDict()
        self.batches["bg"] = pyglet.graphics.Batch()
        self.batches["objects"] = pyglet.graphics.Batch()
        self.batches["player"] = pyglet.graphics.Batch()
        self.batches["fg"] = pyglet.graphics.Batch()
        self.batches["ui_bg"] = pyglet.graphics.Batch()
        self.batches["ui_fg"] = pyglet.graphics.Batch()

        self.log.info("Initializing media player.")
        self.media_player = pyglet.media.Player()
        self.sfx_player = pyglet.media.Player()
        self.sfx_player.eos_action = self.sfx_player.EOS_STOP
        self.bgm_looper = pyglet.media.SourceGroup(
            self.sounds["bgm01"].audio_format, None
        )
        self.bgm_looper.loop = True
        self.log.debug("Queuing background music...")
        self.bgm_looper.queue(self.sounds["bgm01"])
        self.media_player.queue(self.bgm_looper)
        self.media_player.play()    # Playing and pausing the media player
        self.media_player.pause()   # in order to avoid delay on sfx play

        self.log.debug("Loading game editor.")
        self.editor = Editor(self)

        self.shapes = ShapeGenerator()

        self.log.info("Creating physics space.")
        self.phys_space = pymunk.Space()
        self.phys_space.add_collision_handler(
            1, 1, post_solve=self.collision_handler
        )
        self.phys_space.gravity = 0, -(self.cfg["gravity"])

        self.log.debug("Loading background and foreground sprites.")
        entities.BackgroundImage(self)
        entities.GroundBlock(self, x=0, y=0, w=self.width, h=16)
        entities.ForegroundImage(self, 50, 16)
        entities.ForegroundImage(self, 90, 48)
        entities.ForegroundImage(self, 180, 48)

        self.log.info("Spawning static game objects.")

        for i in range(self.width // 4, self.width - self.width // 4, 16):
                entities.Block(self, x=i, y=self.height - 64, w=16, h=16)
        for i in range(self.width // 4, self.width - self.width // 4, 16):
                entities.Block(self, x=i, y=32, w=16, h=16)

        self.log.info("Creating outer boundaries for game area.")
        static_lines = [
            pymunk.Segment(
                self.phys_space.static_body, (0, 15), (self.map_width, 15), 1
            ),
            pymunk.Segment(
                self.phys_space.static_body, (0, 0), (0, self.map_height), 1
            ),
            pymunk.Segment(
                self.phys_space.static_body,
                (self.map_width, 0),
                (self.map_width, self.map_height), 1
            ),
            pymunk.Segment(
                self.phys_space.static_body,
                (0, self.map_height),
                (self.map_width, self.map_height), 1
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

        self.log.info("Spawning player entity.")
        self.player = Player(self)
        entities.Player(self, x=32, y=80)
        self.timer_enabled = False

    def spawn_player(self):
        pass

    def start_systems(self):
        self.add_system(systems.MousePressAreaSystem(self))
        self.add_system(systems.MousePressSystem(self))
        self.add_system(systems.SpritePosSystem(self))
        self.add_system(systems.FloatingSpritePosSystem(self))
        self.add_system(systems.StaticSpritePosSystem(self))
        self.add_system(systems.ParallaxSystem(self))
        self.add_system(systems.DirectionalSpriteSystem(self))
        self.add_system(systems.SpriteBatchSystem(self))
        self.add_system(systems.SoundEffectSystem(self))
        self.add_system(systems.RenderSystem(self))

    def play_sound(self, name):
        s = self.sounds[name]
        s.play()

    def collision_handler(self, space, arbiter):
        if arbiter.is_first_contact:
            self.play_sound("dunk")
        return False

    def add_block(self, x, y, w=16, h=16):
        # entities.Orb(self, x=x, y=y)
        entities.Block(self, x=x, y=y, w=w, h=h)

    def add_bush(self, x, y):
        entities.ForegroundImage(self, x, y)

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
            self.log.debug(
                "No texture with identifier '{0}', \
returning debug texture".format(
                    name
                )
            )
            return self.textures["debug"]

    def load_img(self, filename):
        return pyglet.resource.image(
            os.path.join(TEX_PATH, filename)
        )

    def load_textures(self):
        debug_img = self.load_img("debug.png")
        player_img_l = self.load_img("dumb.png")
        player_img_r = self.load_img("dumb_r.png")
        block_img = self.load_img("block.png")
        tree_img = self.load_img("tree_m.png")
        button_img = self.load_img("button.png")
        # Tiled using Pillow
        ground_img = pyglet.image.ImageData(
            self.map_width - (self.map_width % 16), 16, 'RGB', tile_img(
                os.path.join(TEX_PATH, "ground_grass.png"),
                self.map_width - (self.map_width % 16), 16
            ), pitch=(self.map_width - (self.map_width % 16)) * 3
        ).get_texture()
        bg_img = pyglet.image.ImageData(
            self.map_width + self.width, self.height, 'RGB', tile_img(
                os.path.join(TEX_PATH, "bg.png"),
                self.map_width + self.width, self.height
            ), pitch=(self.map_width + self.width) * 3
        ).get_texture()

        self.textures = dict(
            debug=debug_img,
            player_l=player_img_l,
            player_r=player_img_r,
            block=block_img,
            bg=bg_img,
            ground=ground_img,
            tree_m=tree_img,
            button=button_img,
        )

    def load_sounds(self):
        jump1 = pyglet.resource.media(
            os.path.join(SFX_PATH, "jump1.ogg"), streaming=False
        )
        jump2 = pyglet.resource.media(
            os.path.join(SFX_PATH, "jump2.ogg"), streaming=False
        )
        jump3 = pyglet.resource.media(
            os.path.join(SFX_PATH, "jump3.ogg"), streaming=False
        )
        dunk = pyglet.resource.media(
            os.path.join(SFX_PATH, "dunk.ogg"), streaming=False
        )
        bgm01 = pyglet.resource.media(os.path.join(SFX_PATH, "bgm01.ogg"))

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

        # Editor keys
        if button == k._1:
            self.add_block(
                self.mouse_x - self.offset_x, self.mouse_y
            )
        if button == k._2:
            entities.ForegroundImage(
                self, self.mouse_x - self.offset_x, self.mouse_y
            )

    def on_mouse_press(self, x, y, btn, mod):
        # print(x, y, btn)
        s = self.scale
        if btn == 1:
            self.mouse_click = components.MouseClicked(
                *self.get_gamepos(x, y), "left"
            )
            # self.editor.add_block()
            # self.add_block(
            #     x // s - self.offset_x, y // s
            # )
        elif btn == 4:
            self.mouse_click = components.MouseClicked(
                *self.get_gamepos(x, y), "right"
            )
            self.remove_block(
                x // s - self.offset_x, y // s
            )

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_x, self.mouse_y = self.get_gamepos(x, y)

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
        # self.ground_sprite.x = int(self.offset_x)
        for i in range(30):
            self.phys_space.step(dt / 30)

    def get_pixel_aligned_pos(self, x, y):
        return int(x - (x % SCALING)), int(y - (y % SCALING))

    def get_gamepos(self, x, y):
        return int(x / self.scale), int(y / self.scale)

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
        self.game.log.debug("Setting gl configuration.")
        self.cfg = load_cfg("Window")
        gl_template = pyglet.gl.Config(
            sample_buffers=1,
            samples=2,
            alpha_size=8,
            stencil_size=8
        )
        try:  # to enable multisampling
            self.game.log.debug("Multisampling enabled.")
            gl_config = screen.get_best_config(gl_template)
        except pyglet.window.NoSuchConfigException:
            self.game.log.warning("Failed to enable multisampling.")
            gl_template = pyglet.gl.Config(alpha_size=8)
            gl_config = screen.get_best_config(gl_template)
        gl_context = gl_config.create_context(None)
        self.game.log.info("Initializing main window.")
        super(GameWindow, self).__init__(
            context=gl_context,
            config=gl_config,
            resizable=False,
            vsync=self.cfg["vsync"],
        )

        self.apply_settings()
        # These have seemingly no effects and are just attempts at fixing
        # the blurry texture that happens at random
        glEnable(GL_TEXTURE_2D)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

    def apply_settings(self):
        self.game.log.info("Applying window settings.")
        if not self.fullscreen:
            self.set_location(
                (screen.width - self.cfg["width"]) // 2,
                (screen.height - self.cfg["height"]) // 2
            )
            self.width, self.height = self.cfg["width"], self.cfg["height"]
        self.game.log.debug("Setting GL flags for pixel scaling.")
        s = float(self.cfg["scale"])
        glScalef(s, s, s)

if __name__ == "__main__":
    # Initialize world
    g = GameWorld()

    # Schedule the update function on the world to run every frame.
    pyglet.clock.schedule_interval(g.update, 1.0 / FPS)
    # pyglet.clock.schedule_interval(g.render, 1.0 / FPS)
    pyglet.clock.schedule_interval(g.process, 1.0 / FPS)

    # Initialize pyglet app
    pyglet.app.run()
