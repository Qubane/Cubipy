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
        self.voxels: np.ndarray = np.zeros([CHUNK_SIZE, CHUNK_SIZE, CHUNK_SIZE], dtype=np.uint8)


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
                chunk.voxels[z][y][x] = 1
    return chunk


def generate_debug(infill: float, position: tuple[int, int, int]) -> Chunk:
    """
    Temporary. Generates chunk with randomly placed blocks with a given infill
    :param infill: % of space filled
    :param position: chunk position
    :return: generated chunk
    """

    chunk = Chunk(position)
    for z in range(CHUNK_SIZE):
        for y in range(CHUNK_SIZE):
            for x in range(CHUNK_SIZE):
                if np.random.random() <= infill:
                    chunk.voxels[z][y][x] = 1
    return chunk
