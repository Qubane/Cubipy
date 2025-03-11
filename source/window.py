"""
Window class
"""


import arcade


class Window(arcade.Window):
    """
    Arcade window class
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
