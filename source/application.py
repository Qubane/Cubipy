"""
Application class
"""


from source.window import Window


class Application:
    """
    Application class
    """

    def __init__(
            self,
            win_width: int = 1280,
            win_height: int = 720,
            win_title: str = "window"):
        self.window: Window = Window(win_width, win_height, win_title)

    def run(self):
        ...
