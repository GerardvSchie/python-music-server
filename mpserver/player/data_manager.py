import logging
import os

from mpserver.player.music_player import MusicPlayer
from mpserver.grpc import mmp_pb2
from mpserver.grpc import mmp_pb2_grpc as rpc
from mpserver.utils.event_firing import EventFiring
from mpserver.utils.mmp_response_utils import error_response, empty_response
from mpserver.utils.player_utils import find_song_by_id


class DataManager(rpc.DataManagerServicer, EventFiring):
    def __init__(self, mplayer: MusicPlayer):
        super(DataManager, self).__init__()
        self._mplayer = mplayer

    def DeleteAlbum(self, request, context):
        return super().DeleteAlbum(request, context)

    def DeleteSong(self, request, context):
        return super().DeleteSong(request, context)

    def MoveSong(self, request, context):
        return super().MoveSong(request, context)

    def RenameAlbum(self, request, context):
        return super().RenameAlbum(request, context)

    def RenameSong(self, request: mmp_pb2.RenameData, context):
        new_title = request.new_title
        if not new_title:
            return error_response("No new title for rename")

        _, song = find_song_by_id(self._mplayer.albums, request.id)
        if not song:
            return error_response("Didn't find song by id to rename")

        current_song = self._mplayer.music_queue.current()
        if current_song and current_song.id == song.id:
            return error_response(f"Could not rename song currently playing")

        _, ext = os.path.splitext(song.filepath)
        file_name = os.path.dirname(song.filepath) + os.sep + new_title + ext

        try:
            logging.info(f"Renaming {song.title} to {new_title} ({song.filepath} -> {file_name})")
            os.rename(song.filepath, file_name)
            return empty_response()
            # TODO: don't catch these errors, let upper level work with that
        except OSError:
            return error_response(f"Song with id {request.id} does not exist")
