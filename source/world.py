"""
World related operations
"""


import arcade.gl
import numpy as np
from source.options import *


class World:
    """
    Container for large amount of cubes
    """

    def __init__(self):
        self.voxels: np.ndarray = np.zeros([WORLD_SIZE ** 3], dtype=np.uint8)
        self.buffer: arcade.gl.Buffer | None = None

    def set_unsafe(self, position: tuple[int, int, int], value: int) -> None:
        """
        Sets block at given XYZ to given value.
        Don't use it unless you are sure the position doesn't go over chunk bounds.
        :param position: block position
        :param value: id to set
        """

        self.voxels[position[0] * WORLD_LAYER + position[1] * WORLD_SIZE + position[2]] = value

    def set(self, position: tuple[int, int, int], value: int) -> bool:
        """
        Sets block at given XYZ to given value.
        :param position: block position
        :param value: id to set
        :return: True when block was set, False when block was out of bounds
        """

        if (-1 < position[0] < WORLD_SIZE) and (-1 < position[1] < WORLD_SIZE) and (-1 < position[2] < WORLD_SIZE):
            self.voxels[position[0] * WORLD_LAYER + position[1] * WORLD_SIZE + position[2]] = value
            return True
        return False

    def get_unsafe(self, position: tuple[int, int, int]) -> int:
        """
        Gets block at given XYZ to given value.
        Don't use it unless you are sure the position doesn't go over chunk bounds.
        :param position: block position
        """

        return self.voxels[position[0] * WORLD_LAYER + position[1] * WORLD_SIZE + position[2]]

    def get(self, position: tuple[int, int, int]) -> int:
        """
        Gets block at given XYZ to given value
        :param position: block position
        :return: block id when inbound, -1 when out of bounds
        """

        if (-1 < position[0] < WORLD_SIZE) and (-1 < position[1] < WORLD_SIZE) and (-1 < position[2] < WORLD_SIZE):
            return self.voxels[position[0] * WORLD_LAYER + position[1] * WORLD_SIZE + position[2]]
        return -1


def generate_flat(level: int) -> World:
    """
    Temporary. Generates a flat chunk
    :param level: sea level
    :return: chunk
    """

    world = World()
    for z in range(WORLD_SIZE):
        for x in range(WORLD_SIZE):
            for y in range(0, level):
                world.set_unsafe((x, y, z), 1)
    return world


def generate_debug(infill: float) -> World:
    """
    Temporary. Generates chunk with randomly placed blocks with a given infill
    :param infill: % of space filled
    :return: generated chunk
    """

    world = World()
    voxels = np.random.random(WORLD_SIZE ** 3)
    world.voxels = (np.vectorize(lambda x: x < infill)(voxels)).astype(np.uint8)
    return world
