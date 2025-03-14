"""
Application class
"""


import math
import arcade
from arcade import Vec2, Vec3
from pyglet.event import EVENT_HANDLE_STATE
from source.world import *
from source.classes import *
from source.options import *


class Application(arcade.Window):
    """
    Arcade application class
    """

    def __init__(
            self,
            width: int = 1280,
            height: int = 720,
            title: str = "window",
            gl_ver: tuple[int, int] = (4, 3)):

        super().__init__(
            width, height, title,
            gl_version=gl_ver)

        # graphics
        self.center_window()

        self.shadertoy: arcade.experimental.Shadertoy | None = None
        self.load_shaders()

        # make graphs
        arcade.enable_timings()
        self.perf_graph_list = arcade.SpriteList()

        graph = arcade.PerfGraph(200, 120, graph_data="FPS")
        graph.position = 100, self.height - 60
        self.perf_graph_list.append(graph)

        # temp
        self.chunk: Chunk = generate_debug(0.1)

        # player
        self.player: Player = Player(Vec3(8, 8, 8), Vec2(0, 0))

        # controls
        self.keys: set[int] = set()
        self.set_mouse_visible(False)
        self.set_exclusive_mouse()

    def load_shaders(self):
        """
        Loads shaders
        """

        window_size = self.get_size()

        self.shadertoy = arcade.experimental.Shadertoy.create_from_file(
            window_size,
            f"{SHADER_DIR}/main.glsl")

    # noinspection PyTypeChecker
    def on_draw(self):
        self.use()
        self.clear()

        self.shadertoy.program.set_uniform_safe("CHUNK_SIZE", CHUNK_SIZE)
        self.shadertoy.program.set_uniform_safe("PLR_FOV", self.player.fov)
        self.shadertoy.program.set_uniform_array_safe("PLR_POS", self.player.pos)
        self.shadertoy.program.set_uniform_array_safe("PLR_DIR", self.player.rot)
        self.shadertoy.program.set_uniform_array_safe("CHUNK_DATA", self.chunk.voxels.flatten())

        self.shadertoy.render()

        self.perf_graph_list.draw()

    def on_key_press(self, symbol: int, modifiers: int) -> EVENT_HANDLE_STATE:
        self.keys.add(symbol)

    def on_key_release(self, symbol: int, modifiers: int) -> EVENT_HANDLE_STATE:
        self.keys.discard(symbol)

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> EVENT_HANDLE_STATE:
        self.player.rotate(Vec2(dy, -dx) * self.player.sensitivity)

    def on_update(self, delta_time: float):
        # keyboard movement
        looking_direction: Vec2 = Vec2(math.cos(self.player.rot[1]), math.sin(self.player.rot[1]))
        movement = looking_direction * delta_time * self.player.movement_speed

        if arcade.key.W in self.keys:
            self.player.move(Vec3(-movement.y, movement.x, 0))
        if arcade.key.S in self.keys:
            self.player.move(Vec3(movement.y, -movement.x, 0))
        if arcade.key.A in self.keys:
            self.player.move(Vec3(-movement.x, -movement.y, 0))
        if arcade.key.D in self.keys:
            self.player.move(Vec3(movement.x, movement.y, 0))
        if arcade.key.SPACE in self.keys:
            self.player.move(Vec3(0, 0, delta_time * self.player.movement_speed))
        if arcade.key.LSHIFT in self.keys or arcade.key.RSHIFT in self.keys:
            self.player.move(Vec3(0, 0, -delta_time * self.player.movement_speed))
        if arcade.key.ESCAPE in self.keys:
            exit(0)
