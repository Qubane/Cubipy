"""
Application class
"""


import math
import arcade
import arcade.gl
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
        self.buffer: arcade.context.Framebuffer | None = None
        self.quad: arcade.context.Geometry | None = None
        self.program: arcade.context.Program | None = None
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
        accum = 0
        for z in range(2):
            for y in range(2):
                for x in range(2):
                    self.world.add_chunk(generate_debug(0.025, (x, y, z)))

                    accum += CHUNK_SIZE ** 3
                    print(f"Generated chunk at {(x, y, z)}; voxel count: {accum}")
        self.world_man: ChunkManager = ChunkManager(self.world)
        self.world_man.player = self.player

    def load_shaders(self):
        """
        Loads shaders
        """

        # window size
        window_size = self.get_size()

        # rendering
        self.quad = arcade.gl.geometry.quad_2d_fs()
        self.buffer = self.ctx.framebuffer(
            color_attachments=[self.ctx.texture(window_size, components=4)],
            depth_attachment=self.ctx.depth_texture(window_size))

        # load shaders
        self.program = self.ctx.load_program(
            vertex_shader=f"{SHADER_DIR}/vert.glsl",
            fragment_shader=f"{SHADER_DIR}/main.glsl")

    # noinspection PyTypeChecker
    def on_draw(self):
        # clear buffer
        self.clear()

        # set uniforms that remain the same for on_draw call
        self.program.set_uniform_safe("PLR_FOV", self.player.fov)
        self.program.set_uniform_array_safe("iResolution", (*self.size, 1.0))
        self.program.set_uniform_array_safe("PLR_POS", self.player.pos)
        self.program.set_uniform_array_safe("PLR_DIR", self.player.rot)

        # enable blending and depth testing
        self.ctx.enable(self.ctx.BLEND)
        # self.ctx.enable(self.ctx.DEPTH_TEST, self.ctx.BLEND)

        # go through managed chunks and render them
        ssbo_list = []
        for chunk in self.world_man:
            ssbo_list.append(self.ctx.buffer(data=chunk.voxels.flatten(), usage="stream"))
        for idx, chunk in enumerate(self.world_man):
            chunk: Chunk

            # set player camera position relative to chunk
            self.program.set_uniform_array_safe(
                "PLR_POS", self.player.pos + Vec3(*chunk.position) * CHUNK_SIZE)

            # bind storage buffer with chunk data
            ssbo_list[idx].bind_to_storage_buffer(binding=0)

            # render image to quad
            self.quad.render(self.program)

        # # disable depth testing
        # self.ctx.disable(self.ctx.DEPTH_TEST)

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
