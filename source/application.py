"""
Application class
"""


import arcade


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

        # make graphs
        arcade.enable_timings()
        self.perf_graph_list = arcade.SpriteList()

        graph = arcade.PerfGraph(200, 120, graph_data="FPS")
        graph.position = 100, self.height - 60
        self.perf_graph_list.append(graph)

    def on_draw(self):
        self.clear()

        self.perf_graph_list.draw()
