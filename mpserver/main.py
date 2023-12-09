import logging
from datetime import datetime

import mpserver.utils.logger as logger
from mpserver.player.music_server import MusicServer


def main():
    # print("\tMelonMusicPlayer made by Melle Dijkstra © " + str(datetime.now().year))
    # print("\tVersion: 3")

    music_server = MusicServer()
    try:
        music_server.serve()
    except KeyboardInterrupt:
        logging.info("Aborting MelonMusicPlayer")

    music_server.shutdown()


if __name__ == '__main__':
    logger.initialize()
    main()
