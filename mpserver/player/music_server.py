from concurrent import futures
import grpc
import logging

from mpserver.grpc import mmp_pb2_grpc as rpc
from mpserver.player.data_manager import DataManager
from mpserver.player.music_player import MusicPlayer
from mpserver.utils.config_parser import MusicServerConfigParser as ConfigParser
from mpserver.utils.event_firing import EventFiring


class MusicServer(EventFiring):
    """
    The Music Server which the client apps connects with.
    It sets up all the different components and a gRPC server
    """
    def __init__(self):
        super(MusicServer, self).__init__()
        self._event_callbacks = {}
        for attribute in [attr for attr in dir(self.Events()) if not callable(attr) and not attr.startswith("__")]:
            self._event_callbacks[attribute] = []

        # Setup server components and gRPC server
        self._mplayer = MusicPlayer()
        self._data_manager = DataManager(self._mplayer)
        self._gserver = self.__setup_gserver()

    def __setup_gserver(self):
        gserver = grpc.server(futures.ThreadPoolExecutor(max_workers=ConfigParser.max_connections()))
        rpc.add_MusicPlayerServicer_to_server(self._mplayer, gserver)
        rpc.add_DataManagerServicer_to_server(self._data_manager, gserver)
        gserver.add_insecure_port(f"[::]:{ConfigParser.port()}")
        return gserver

    def serve(self):
        # This method starts the music server and listens for incoming connections
        cmd = ''
        self._gserver.start()
        logging.info(f"gRPC Server started (port={ConfigParser.port()})")
        while cmd != "exit":
            # cmd = input("$-> ")
            pass
        self._gserver.stop(0)

    def shutdown(self):
        logging.info("Shutting down gRPC Server")
        self._mplayer._player.shutdown()
        self._mplayer.close_streams = True
        if self._gserver:
            self._gserver.stop(0)
