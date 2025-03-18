"""
Some of the rendering related things are put here
"""


import arcade.gl
from source.world import *
from source.classes import *


class ChunkMemory:
    """
    Manages chunk related things
    """

    player: Player | None = None
    context: arcade.context.Context | None = None

    def __init__(self, world: World):
        self.world: World = world
        self.chunk_list: list[tuple[Chunk, arcade.gl.Buffer]] = []

    def _generate_mapping(self):
        """
        Generates a chunk+buffer list
        """

        for chunk in self.world.chunks.values():
            self.chunk_list.append((chunk, self.context.buffer(data=chunk.voxels, usage="static")))

    def __iter__(self):
        if self.context is None:
            self.context = arcade.get_window().ctx
            self._generate_mapping()

        self.chunk_list.sort(key=lambda x: self.player.pos.distance(x[0].position), reverse=True)

        return self.chunk_list.__iter__()
