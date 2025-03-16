"""
Application class
"""


import math
import arcade
from pyglet.event import EVENT_HANDLE_STATE
from source.world import *
from source.classes import *
from source.options import *
from source.rendering import *


class Application(arcade.Window):
    """
    Arcade application class
    """

    def __init__(
            self,
            width: int = 1440,
            height: int = 810,
            title: str = "window",
            gl_ver: tuple[int, int] = (4, 3)):

        super().__init__(
            width, height, title,
            gl_version=gl_ver)

        # center the window
        self.center_window()

        # shader related things
        self.shadertoy: arcade.experimental.Shadertoy | None = None
        self.load_shaders()

        # make graphs
        arcade.enable_timings()
        self.perf_graph_list = arcade.SpriteList()

        # add fps graph
        graph = arcade.PerfGraph(200, 120, graph_data="FPS")
        graph.position = 100, self.height - 60
        self.perf_graph_list.append(graph)

        # player
        self.player: Player = Player(Vec3(8, 8, 8), Vec2(0, 90))

        # player movement
        self.keys: set[int] = set()
        self.set_mouse_visible(False)
        self.set_exclusive_mouse()

        # world
        self.world: World = World()
        for i in range(5):
            for j in range(5):
                chunk = generate_debug((i + j + 1) / 9, (i, j, 0))
                self.world.add_chunk(chunk)
                print(f"Generated chunk at {chunk.position}")
        self.world_man: ChunkManager = ChunkManager(self.world)
        self.world_man.player = self.player

    def load_shaders(self):
        """
        Loads shaders
        """

        # window size
        window_size = self.get_size()

        # load shaders
        self.shadertoy = arcade.experimental.Shadertoy.create_from_file(
            window_size,
            f"{SHADER_DIR}/main.glsl")

    # noinspection PyTypeChecker
    def on_draw(self):
        # clear buffer
        self.clear()

        # set uniforms that remain the same for on_draw call
        self.shadertoy.program.set_uniform_safe("PLR_FOV", self.player.fov)
        self.shadertoy.program.set_uniform_array_safe("PLR_POS", self.player.pos)
        self.shadertoy.program.set_uniform_array_safe("PLR_DIR", self.player.rot)

        # enable blending and depth testing
        self.ctx.enable(self.ctx.DEPTH_TEST, self.ctx.BLEND)

        # go through managed chunks and render them
        for chunk in self.world_man:
            self.shadertoy.program.set_uniform_array_safe(
                "PLR_POS", self.player.pos + Vec3(*chunk.position) * CHUNK_SIZE)
            self.shadertoy.program["CHUNK_DATA"] = chunk.voxels.flatten()
            self.shadertoy.render()

        # disable depth testing for graphs
        self.ctx.disable(self.ctx.DEPTH_TEST)

        # draw performance graphs
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
            arcade.exit()
