"""
Classes definitions
"""


from typing import Iterable
from arcade import Vec2, Vec3


class Player:
    def __init__(self, position: Vec3, rotation: Vec2):
        self.pos: Vec3 = position
        self.rot: Vec2 = rotation

    def move(self, offset: Vec3):
        self.pos += offset

    def rotate(self, offset: Vec2):
        self.rot += offset
