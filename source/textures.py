"""
Texture manager
"""


import arcade
from source.options import *


class TextureManager:
    """
    Manages textures
    """

    def __init__(self):
        self.texture_list: list[arcade.context.Texture2D] = []
        self._named_mapping: dict[str, dict[str, int]] = {}

        self.block_texture_mapping: dict[int, dict[str, int | dict]] = {}
