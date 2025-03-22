"""
Main file
"""


from source.application import Application
from source.options import WINDOW_RESOLUTION


def main():
    app = Application(*WINDOW_RESOLUTION, title="Cubipy")
    app.run()


if __name__ == '__main__':
    main()
