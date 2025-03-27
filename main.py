"""
Main file
"""


from source.application import Application
from source.options import GAME_TITLE, WINDOW_RESOLUTION


def main():
    app = Application(*WINDOW_RESOLUTION, GAME_TITLE)
    app.run()


if __name__ == '__main__':
    main()
