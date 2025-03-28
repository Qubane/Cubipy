"""
Block lookup table
"""


class Blocks:
    """
    Some lookups for blocks
    """

    named: dict[str, int] = {}

    @classmethod
    def initialize(cls):
        """
        Initializes blocks
        """
