"""
World related operations
"""


from PIL import Image
import arcade.gl
import numpy as np
from numpy import ndarray

from source.options import *


class World:
    """
    Container for large amount of cubes
    """

    def __init__(self):
        self.voxels: np.ndarray = np.zeros(WORLD_SIZE ** 3, dtype=np.uint8)
        self.buffer: arcade.gl.Buffer | None = None

    def set_unsafe(self, position: tuple[int, int, int], value: int) -> None:
        """
        Sets block at given XYZ to given value.
        Don't use it unless you are sure the position doesn't go over chunk bounds.
        :param position: block position
        :param value: id to set
        """

        self.voxels[position[2] * WORLD_LAYER + position[1] * WORLD_SIZE + position[0]] = value

    def set(self, position: tuple[int, int, int], value: int) -> bool:
        """
        Sets block at given XYZ to given value.
        :param position: block position
        :param value: id to set
        :return: True when block was set, False when block was out of bounds
        """

        if (-1 < position[0] < WORLD_SIZE) and (-1 < position[1] < WORLD_SIZE) and (-1 < position[2] < WORLD_SIZE):
            self.voxels[position[2] * WORLD_LAYER + position[1] * WORLD_SIZE + position[0]] = value
            return True
        return False

    # noinspection PyTypeChecker
    def get_unsafe(self, position: tuple[int, int, int]) -> int:
        """
        Gets block at given XYZ to given value.
        Don't use it unless you are sure the position doesn't go over chunk bounds.
        :param position: block position
        """

        return self.voxels[position[2] * WORLD_LAYER + position[1] * WORLD_SIZE + position[0]]

    # noinspection PyTypeChecker
    def get(self, position: tuple[int, int, int]) -> int:
        """
        Gets block at given XYZ to given value
        :param position: block position
        :return: block id when inbound, -1 when out of bounds
        """

        if (-1 < position[0] < WORLD_SIZE) and (-1 < position[1] < WORLD_SIZE) and (-1 < position[2] < WORLD_SIZE):
            return self.voxels[position[2] * WORLD_LAYER + position[1] * WORLD_SIZE + position[0]]
        return -1


def generate_flat(level: int) -> World:
    """
    Temporary. Generates a flat chunk
    :param level: sea level
    :return: chunk
    """

    world = World()
    for y in range(WORLD_SIZE):
        for x in range(WORLD_SIZE):
            for z in range(level):
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


def generate_landscape(level: int, magnitude: float) -> World:
    """
    Temporary. Generates simple landscape
    :param level: sea level
    :param magnitude: magnitude
    :return: generated chunk
    """

    octet_count = 6

    noise = [np.random.random((x * 2) ** 2).astype(np.float64) for x in range(2, octet_count * 2 + 2)]
    height_map = np.zeros([WORLD_SIZE ** 2], dtype=np.float64)

    for octet in range(octet_count):
        octet_size = octet * 2 + 2
        for oct_y in range(octet_size):
            for oct_x in range(octet_size):
                plotting_size = WORLD_SIZE // octet_size
                for y in range(plotting_size):
                    for x in range(plotting_size):
                        hm_index = (y + oct_y * plotting_size) * WORLD_SIZE + (x + oct_x * plotting_size)
                        height_map[hm_index] += noise[octet][oct_y * octet_size + oct_x]
    height_map /= octet_count

    Image.fromarray((height_map * 255).astype(np.uint8).reshape([WORLD_SIZE, WORLD_SIZE])).save("height.png")

    world = World()
    for y in range(WORLD_SIZE):
        for x in range(WORLD_SIZE):
            height = int((height_map[y * WORLD_SIZE + x] - 0.5) * magnitude + level)
            for z in range(height):
                world.set_unsafe((x, y, z), 1)
    return world
