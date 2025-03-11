"""
Application class
"""


import arcade
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

        # center the window
        self.center_window()

        self.shadertoy: arcade.experimental.Shadertoy | None = None
        self.load_shaders()

        # make graphs
        arcade.enable_timings()
        self.perf_graph_list = arcade.SpriteList()

        graph = arcade.PerfGraph(200, 120, graph_data="FPS")
        graph.position = 100, self.height - 60
        self.perf_graph_list.append(graph)

    def load_shaders(self):
        """
        Loads shaders
        """

        window_size = self.get_size()

        self.shadertoy = arcade.experimental.Shadertoy.create_from_file(
            window_size,
            f"{SHADER_DIR}/main.glsl")

    def on_draw(self):
        self.use()
        self.clear()

        self.shadertoy.render()

        self.perf_graph_list.draw()
