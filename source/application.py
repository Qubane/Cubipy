"""
Application class
"""


import os
import arcade
import arcade.gl
from PIL import Image, ImageOps
from pyglet.event import EVENT_HANDLE_STATE
from source.world import *
from source.classes import *
from source.options import *
from source.textures import *


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
        self.screenshot_buffer: arcade.context.Framebuffer | None = None
        self.quad: arcade.context.Geometry | None = None
        self.program: arcade.context.Program | None = None
        self.load_shaders()

        self.texture_manager: TextureManager = TextureManager()
        self.texture_manager.load_textures()
        self.texture_manager.generate_raw_texture_mapping()

        # make graphs
        arcade.enable_timings()
        self.perf_graph_list = arcade.SpriteList()

        # add fps graph
        graph = arcade.PerfGraph(200, 120, graph_data="FPS")
        graph.position = 100, self.height - 60
        self.perf_graph_list.append(graph)

        # player
        self.player: Player = Player(Vec3(WORLD_CENTER, WORLD_CENTER, WORLD_CENTER), Vec2(0, 90))

        # player movement
        self.keys: set[int] = set()
        self.set_mouse_visible(False)
        self.set_exclusive_mouse()

        # world
        debug_world_name = f"{SAVES_DIR}/debug.npy"
        self.world: World = World()
        if not os.path.isfile(debug_world_name):
            self.world: World = WorldGen.generate_landscape(WORLD_SIZE // 2, 32)
            self.world.save(debug_world_name)
        else:
            self.world.load(debug_world_name)
        self.world_buffer = self.ctx.buffer(data=self.world.voxels, usage="static")

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

        self.screenshot_buffer = self.ctx.framebuffer(
            color_attachments=[self.ctx.texture(SCREENSHOT_RESOLUTION, components=3)])

        # load shaders
        self.program = self.ctx.load_program(
            vertex_shader=f"{SHADER_DIR}/vert.glsl",
            fragment_shader=f"{SHADER_DIR}/main.glsl")

    # noinspection PyTypeChecker
    def take_screenshot(self):
        """
        Takes a high resolution screenshot
        """

        self.program.set_uniform_array_safe("u_resolution", (*SCREENSHOT_RESOLUTION, 1.0))
        with self.screenshot_buffer.activate():
            self.render_pass()

        img = Image.frombytes("RGB", SCREENSHOT_RESOLUTION, self.screenshot_buffer.read())
        ImageOps.flip(img).save(f"{SAVES_DIR}/capture.png")

    # noinspection PyTypeChecker
    def render_pass(self):
        """
        Render pass without any buffer changes
        """

        # clear buffer
        self.clear()

        # set uniforms that remain the same for on_draw call
        self.program.set_uniform_safe("u_playerFov", self.player.fov)
        self.program.set_uniform_array_safe("u_playerPosition", self.player.pos)
        self.program.set_uniform_array_safe("u_playerDirection", self.player.rot)
        self.program.set_uniform_array_safe("u_worldSun", self.world.sun)
        self.program.set_uniform_array_safe("u_textureMapping", self.texture_manager.raw_texture_mapping)

        # bind texture array
        self.program.set_uniform_safe("u_textureArray", 0)
        self.texture_manager.texture_array.use(0)

        # bind storage buffer with chunk data
        self.world_buffer.bind_to_storage_buffer(binding=0)

        # render image to quad
        self.quad.render(self.program)

    # noinspection PyTypeChecker
    def on_draw(self):
        # use main screen buffer
        self.buffer.activate()  # context manager doesn't work here for some reason? But works without it
        self.program.set_uniform_array_safe("u_resolution", (*self.size, 1.0))
        self.render_pass()

        # draw performance graphs
        self.perf_graph_list.draw()

    def on_key_press(self, symbol: int, modifiers: int) -> EVENT_HANDLE_STATE:
        self.keys.add(symbol)

        if symbol == arcade.key.F12:
            self.take_screenshot()

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
