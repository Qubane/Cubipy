"""
Texture manager
"""


import os
import json
import glob
import arcade
import arcade.gl
import numpy as np
from source.options import *


class TextureManager:
    """
    Manages textures
    """

    def __init__(self):
        self.ctx: arcade.context.ArcadeContext = arcade.get_window().ctx
        self.texture_array: arcade.gl.TextureArray | None = None

        self.texture_list: list[arcade.context.Texture2D] = []
        self._named_mapping: dict[str, dict[str, int]] = {}

        self.block_texture_mapping: dict[int, dict[str, int | dict]] = {}

        self.raw_texture_mapping: np.ndarray | None = None

    def load_textures(self):
        """
        Loads textures
        """

        # create texture array
        texture_size = 0
        texture_amount = 0

        # iterate through assets
        configs = []
        for file in glob.glob(TEXTURE_DIR + "/**/*", recursive=True):
            # skip directories
            if os.path.isdir(file):
                continue

            # make file and texture paths
            filepath = file.replace("\\", "/")
            texture_path = filepath[len(TEXTURE_DIR) + 1:].split("/")

            # skip .json for now
            if os.path.splitext(file)[1] == ".json":
                configs.append(filepath)
                continue

            # if category doesn't exist -> make one
            if texture_path[0] not in self._named_mapping:
                self._named_mapping[texture_path[0]] = {}

            # load image
            texture = self.ctx.load_texture(filepath, filter=(self.ctx.NEAREST, self.ctx.NEAREST))

            # append to texture list
            self.texture_list.append(texture)

            # use the index of list
            self._named_mapping[texture_path[0]].update(
                {os.path.splitext(texture_path[1])[0]: len(self.texture_list) - 1})

            # count textures
            texture_size = max(texture_size, texture.width)
            texture_amount += 1

        for config in configs:
            with open(config, "r", encoding="ascii") as f:
                config_data = json.load(f)
            self.block_texture_mapping[config_data["id"]] = config_data

        # fill it with textures
        texture_data = b''
        for level, texture in enumerate(self.texture_list):
            texture_data += texture.read()

        # create texture array
        self.texture_array = self.ctx.texture_array(
            (texture_size, texture_size, texture_amount),
            filter=(self.ctx.NEAREST, self.ctx.NEAREST),
            data=texture_data)

    def generate_raw_texture_mapping(self):
        """
        Generates 'self.raw_texture_mapping' via
        """

        self.raw_texture_mapping = np.zeros(256 * 6, dtype=np.uint32)
