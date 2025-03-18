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

    def _chunk_sorting_method(self, data: tuple[Chunk, arcade.gl.Buffer]) -> float:
        """
        Internal method used to sort chunks
        """

        sq_d = (
            self.player.pos.x - (data[0].position[0] * CHUNK_SIZE - CHUNK_CENTER),
            self.player.pos.y - (data[0].position[1] * CHUNK_SIZE - CHUNK_CENTER),
            self.player.pos.z - (data[0].position[2] * CHUNK_SIZE - CHUNK_CENTER))

        return (sq_d[0]*sq_d[0] + sq_d[1]*sq_d[1] + sq_d[2]*sq_d[2]) ** 0.5

    def __iter__(self):
        if self.context is None:
            self.context = arcade.get_window().ctx
            self._generate_mapping()

        self.chunk_list.sort(key=self._chunk_sorting_method, reverse=True)

        return self.chunk_list.__iter__()
