"""
Block lookup table
"""


import os
import json
import glob
from source.options import *


class Blocks:
    """
    Some lookups for blocks
    """

    # name to id
    named: dict[str, int] = {}

    # id to name
    numbered: dict[int, str] = {}

    @classmethod
    def initialize(cls):
        """
        Initializes blocks
        """

        # iterate over blocks
        for file in glob.glob(f"{TEXTURE_DIR}/blocks/**/*", recursive=True):
            # skip directories
            if os.path.isdir(file):
                continue

            # skip all non-json files
            if os.path.splitext(file)[1] != ".json":
                continue

            # process the block configs
            with open(file, "r", encoding="ascii") as f:
                config = json.load(f)

            cls.named[config["name"]] = config["id"]
            cls.numbered[config["id"]] = config["name"]


Blocks.initialize()
