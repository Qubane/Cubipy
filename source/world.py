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


