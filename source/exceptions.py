"""
Any custom exception types
"""


class GameException(Exception):
    """
    Game related exceptions
    """


class WorldGenSizeError(GameException):
    """
    Error relating to incorrect world size
    """
