"""
Application class
"""


import os
import json
import glob
import arcade
import arcade.gl
from PIL import Image, ImageOps
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

        self.textures: dict[str, dict[str, arcade.context.Texture2D]] = {}
        self.texture_table: dict[int, dict[str, int | dict]] = {}
        self.block_texture_array: arcade.gl.TextureArray | None = None
        self.load_textures()

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

    def load_textures(self):
        """
        Loads textures
        """

        # iterate through assets
        configs = []
        for file in glob.glob(TEXTURE_DIR + "/**/*", recursive=True):
            # skip directories
            if os.path.isdir(file):
                continue

            # make file and texture paths
            filepath = file.replace("\\", "/")
            texture_path = filepath[len(TEXTURE_DIR)+1:].split("/")

            # skip .json for now
            if os.path.splitext(file)[1] == ".json":
                configs.append(filepath)
                continue

            # if category doesn't exist -> make one
            if texture_path[0] not in self.textures:
                self.textures[texture_path[0]] = {}

            texture = self.ctx.load_texture(filepath)
            self.textures[texture_path[0]].update({os.path.splitext(texture_path[1])[0]: texture})

        for config in configs:
            with open(config, "r", encoding="ascii") as f:
                config_data = json.load(f)

            self.texture_table[config_data["id"]] = config_data

        print(self.textures)
        print(self.texture_table)

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

        # bind texture array
        self.program.set_uniform_safe("u_textureArray", 0)
        self.block_texture_array.use(0)

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
