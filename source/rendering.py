"""
Some of the rendering related things are put here
"""


from source.world import *
from source.classes import *


class ChunkManager:
    """
    Manages chunk related things
    """

    player: Player | None = None

    def __init__(self, world: World):
        self.world: World = world

    def __iter__(self):
        # temporary code
        return self.world.chunks.items().__iter__()
