"""
Classes definitions
"""


import math
from arcade import Vec2, Vec3


class Player:
    def __init__(self, position: Vec3, rotation: Vec2, aov: float = 90):
        self.pos: Vec3 = position
        self.rot: Vec2 = rotation
        self.fov: float = 1 / math.tan(math.radians(aov) / 2)

        self.movement_speed: float = 16
        self.sensitivity: float = 0.001

    def move(self, offset: Vec3):
        self.pos += offset

    def rotate(self, offset: Vec2):
        self.rot += offset
