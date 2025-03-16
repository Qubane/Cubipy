"""
World related operations
"""


import numpy as np
from source.options import *


class Chunk:
    """
    16x16x16 block chunk container
    """

    def __init__(self, position: tuple[int, int, int]):
        self.position: tuple[int, int, int] = position
        self.voxels: np.ndarray = np.zeros([CHUNK_SIZE ** 3], dtype=np.uint8)

    def set_unsafe(self, position: tuple[int, int, int], value: int) -> None:
        """
        Sets block at given XYZ to given value
        :param position: block position
        :param value: id to set
        """

    def set(self, position: tuple[int, int, int], value: int) -> None:
        """
        Sets block at given XYZ to given value
        :param position: block position
        :param value: id to set
        """

    def get_unsafe(self, position: tuple[int, int, int]) -> int:
        """
        Gets block at given XYZ to given value
        :param position: block position
        """

    def get(self, position: tuple[int, int, int]) -> int:
        """
        Gets block at given XYZ to given value
        :param position: block position
        """


class World:
    """
    Contains multiple chunks
    """

    def __init__(self):
        self.chunks: dict[int, Chunk] = {}

    def add_chunk(self, chunk: Chunk) -> None:
        """
        Adds chunk to world
        :param chunk: chunk to add
        """

        name = chunk.position[2] * 1_00_00 + chunk.position[1] * 1_00 + chunk.position[0]
        self.chunks[name] = chunk


def generate_flat(level: int, position: tuple[int, int, int]) -> Chunk:
    """
    Temporary. Generates a flat chunk
    :param level: sea level
    :param position: chunk position
    :return: chunk
    """

    chunk = Chunk(position)
    for y in range(CHUNK_SIZE):
        for x in range(CHUNK_SIZE):
            for z in range(0, level):
                chunk.set((x, y, z), 1)
    return chunk


def generate_debug(infill: float, position: tuple[int, int, int]) -> Chunk:
    """
    Temporary. Generates chunk with randomly placed blocks with a given infill
    :param infill: % of space filled
    :param position: chunk position
    :return: generated chunk
    """

    chunk = Chunk(position)
    chunk.voxels = np.random.randint(0, 1, CHUNK_SIZE ** 3)
    return chunk
