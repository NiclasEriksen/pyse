import pymunk
import pyglet.sprite
import random
import math


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


def cpflerpconst(f1, f2, d):
    """Linearly interpolate from f1 to f2 by no more than d."""
    return f1 + cpfclamp(f2 - f1, -d, d)


def cpfclamp(f, min_, max_):
    """Clamp f between min and max"""
    return min(max(f, min_), max_)


class Player:

    def __init__(self, game):
        self.game = game
        self.x, self.y = self.game.width // 2, self.game.height // 2
        self.sprite = pyglet.sprite.Sprite(
            game.textures["player_r"],
            x=self.x, y=self.y,
            batch=self.game.batches["player"], subpixel=False
        )
        # self.sprite.scale = SCALING
        self.direction = dict(
            left=False,
            right=False,
            up=False
        )
        w, h = self.sprite.width, self.sprite.height
        # print("w:{0} h:{1}".format(w, h))
        # self.sprite.width = 256
        # self.sprite.height = 256
        mass = 5
        inertia = pymunk.inf
        self.phys_body = pymunk.Body(mass, inertia)
        self.phys_body.position = self.x, self.y
        self.grounding = {
            'normal': pymunk.vec2d.Vec2d.zero(),
            'penetration': pymunk.vec2d.Vec2d.zero(),
            'impulse': pymunk.vec2d.Vec2d.zero(),
            'position': pymunk.vec2d.Vec2d.zero(),
            'body': None
        }
        self.well_grounded = False
        self.jump_cd = 0.3
        self.jump_cd_timer = 0.
        self.shape = pymunk.Circle(self.phys_body, w / 2, (w / 2, w / 2))
        self.shape.collision_type = 1
        # self.shape.friction = 0
        self.shape.elasticity = 0.
        self.shape.group = 0
        self.game.phys_space.add(self.phys_body, self.shape)

    def jump(self, ground_velocity):
        if self.direction["up"]:
            if self.well_grounded and self.jump_cd_timer <= 0:
                # self.direction["up"] = False
                self.jump_cd_timer = self.jump_cd
                # print("JUMP")
                try:
                    self.game.play_sound(
                        "jump{0}".format(random.randint(1, 3))
                    )
                except:
                    print("Error playing sound")
                jump_v = math.sqrt(
                    2.0 * JUMP_HEIGHT * abs(self.game.phys_space.gravity.y)
                )
                self.phys_body.velocity.y = ground_velocity.y + jump_v
                # self.phys_body.apply_impulse((0, 2500))
        else:
            self.phys_body.velocity.y = min(
                self.phys_body.velocity.y, JUMP_CUTOFF_VELOCITY
            )

    def move(self, dt):
        if self.direction["right"]:
            self.phys_body.velocity.x += 5000 * dt
        if self.direction["left"]:
            self.phys_body.velocity.x -= 5000 * dt

    def update(self, dt):
        self.grounding = {
            'normal': pymunk.vec2d.Vec2d.zero(),
            'penetration': pymunk.vec2d.Vec2d.zero(),
            'impulse': pymunk.vec2d.Vec2d.zero(),
            'position': pymunk.vec2d.Vec2d.zero(),
            'body': None
        }
        # find out if player is standing on ground

        def f(arbiter):
            n = -arbiter.contacts[0].normal
            # print(n.y, self.grounding["normal"].y)
            # print(dir(n))
            if n.y > self.grounding['normal'].y:
                self.grounding['normal'] = n
                self.grounding['penetration'] = -arbiter.contacts[0].distance
                self.grounding['body'] = arbiter.shapes[1].body
                self.grounding['impulse'] = arbiter.total_impulse
                self.grounding['position'] = arbiter.contacts[0].position
        self.phys_body.each_arbiter(f)

        # old_state = self.well_grounded
        # f = self.phys_body.shapes.pop().friction
        if (
            self.grounding['body'] is not None and
            abs(
                self.grounding['normal'].x / self.grounding['normal'].y
            ) < self.shape.friction
        ):
            self.well_grounded = True
        else:
            self.well_grounded = False

        ground_velocity = pymunk.vec2d.Vec2d.zero()
        if self.well_grounded:
            ground_velocity = self.grounding["body"].velocity

        target_vx = 0

        direction = 0

        if self.phys_body.velocity.x > .01:
            direction = 1
        if self.phys_body.velocity.x < -.01:
            direction = -1

        if self.direction["left"]:
            direction = -1
            target_vx -= PLAYER_VELOCITY
        if self.direction["right"]:
            direction = 1
            target_vx += PLAYER_VELOCITY

        self.shape.surface_velocity = target_vx, 0

        if self.grounding["body"] is not None:
            self.shape.friction = (
                -PLAYER_GROUND_ACCEL / self.game.phys_space.gravity.y
            )
        else:
            self.shape.friction = 0.

        if self.grounding["body"] is None:
            self.phys_body.velocity.x = cpflerpconst(
                self.phys_body.velocity.x,
                target_vx + ground_velocity.x,
                PLAYER_AIR_ACCEL * dt
            )

        self.phys_body.velocity.y = max(
            self.phys_body.velocity.y, -FALL_VELOCITY
        )

        self.jump(ground_velocity)
        self.jump_cd_timer -= dt
        # self.move(dt)
        # self.sprite.rotation = math.degrees(-self.phys_body.angle)
        if direction < 0:
            self.sprite.image = self.game.textures["player_l"]
        elif direction > 0:
            self.sprite.image = self.game.textures["player_r"]
        x, y = self.phys_body.position
        self.x = int(round(x))
        self.sprite.y = self.y = int(round(y))
