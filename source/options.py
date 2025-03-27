"""
Configuration file
"""


import os


GAME_TITLE = "Pythagonal"

ASSETS_DIR: str = "assets"
SHADER_DIR: str = f"{ASSETS_DIR}/shaders"
TEXTURE_DIR: str = f"{ASSETS_DIR}/textures"

SAVES_DIR: str = "saves"  # not guaranteed to be created
if not os.path.isdir(SAVES_DIR):
    os.makedirs(SAVES_DIR)

WORLD_SIZE: int = 512
WORLD_LAYER: int = WORLD_SIZE ** 2
WORLD_CENTER: int = WORLD_SIZE // 2

WINDOW_RESOLUTION: tuple[int, int] = (16 * 90, 9 * 90)
SCREENSHOT_RESOLUTION: tuple[int, int] = (3840, 2160)
