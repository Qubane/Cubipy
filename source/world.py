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
        self.voxels: np.ndarray = np.zeros([CHUNK_SIZE, CHUNK_SIZE, CHUNK_SIZE], dtype=np.uint32)


def generate_flat(level: int) -> Chunk:
    """
    Temporary. Generates a flat chunk
    :param level: sea level
    :return: chunk
    """

    chunk = Chunk((0, 0, 0))
    for z in range(CHUNK_SIZE):
        for x in range(CHUNK_SIZE):
            for y in range(0, level):
                chunk.voxels[x][y][z] = 1
    return chunk
