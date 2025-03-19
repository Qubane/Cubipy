"""
World related operations
"""


import os
import arcade.gl
import numpy as np
from scipy.ndimage import zoom
from source.options import *


class World:
    """
    Container for large amount of cubes
    """

    def __init__(self):
        self.voxels: np.ndarray = np.zeros(WORLD_SIZE ** 3, dtype=np.uint8)
        self.buffer: arcade.gl.Buffer | None = None

        self.sun: tuple[float, float, float] = (1, 2, -2)
        length = (self.sun[0]**2 + self.sun[1]**2 + self.sun[2]**2) ** 0.5
        self.sun = (self.sun[0] / length, self.sun[1] / length, self.sun[2] / length)

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

    def save(self, filename: str):
        """
        Saves the world to file with given name.
        :param filename: name of the file
        """

        np.savez_compressed(filename, self.voxels)

    def load(self, filename: str) -> None:
        """
        Loads the world from a file with given name.
        :param filename: name of the file
        """

        self.voxels = np.load(filename)


class WorldGen:
    """
    World generation
    """

    @staticmethod
    def generate_flat(level: int) -> World:
        """
        Generates a flat chunk
        :param level: sea level
        :return: generated world
        """

        world = World()
        for y in range(WORLD_SIZE):
            for x in range(WORLD_SIZE):
                for z in range(level):
                    world.set_unsafe((x, y, z), 1)
        return world

    @staticmethod
    def generate_debug(infill: float) -> World:
        """
        Generates chunk with randomly placed blocks with a given infill
        :param infill: % of space filled
        :return: generated world
        """

        world = World()
        voxels = np.random.random(WORLD_SIZE ** 3)
        world.voxels = (np.vectorize(lambda x: x < infill)(voxels)).astype(np.uint8)
        return world

    @staticmethod
    def generate_landscape(level: int, magnitude: float) -> World:
        """
        Generates simple landscape
        :param level: sea level
        :param magnitude: magnitude
        :return: generated world
        """

        print("Generating height map...")
        octets = [
            (2, 0.05),
            (4, 0.05),
            (8, 0.2),
            (16, 0.2),
            (32, 0.5)]
        height_map = np.zeros([WORLD_SIZE, WORLD_SIZE], dtype=np.float64)
        for octet, influence in octets:
            temp_height_map = np.random.random([WORLD_SIZE // octet, WORLD_SIZE // octet]).astype(np.float64)
            height_map += zoom(temp_height_map, octet) * influence
        print("done;\n")

        print("Putting in the blocks...")
        world = World()
        for y in range(WORLD_SIZE):
            for x in range(WORLD_SIZE):
                height = int((height_map[y][x] - 0.5) * magnitude + level)
                for z in range(height):
                    world.set_unsafe((x, y, z), 1)
            if y % (WORLD_SIZE // 25) == 0:
                print(f"{y / WORLD_SIZE * 100:.2f}% done;")
        print("done;\n")

        return world
