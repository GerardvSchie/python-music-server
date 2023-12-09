import time
import logging

from mpserver.datastructure.music_queue import MusicQueue
from mpserver.grpc import mmp_pb2
from mpserver.grpc import mmp_pb2_grpc as rpc
from mpserver.player.vlc_player import VLCPlayer
from mpserver.utils.mmp_response_utils import error_response, ok_response, empty_response
from mpserver.utils.player_utils import get_albums_and_songs, find_album_by_id, find_song_by_id


class MusicPlayer(rpc.MusicPlayerServicer):
    albums = get_albums_and_songs()
    close_streams = False
    last_update_time = 0
    music_queue = MusicQueue()

    def __init__(self):
        super(MusicPlayer, self).__init__()
        self._player: VLCPlayer = VLCPlayer(self.music_queue, self.__on_finish)

    def __on_finish(self):
        play_next = self._player.play_next()
        if not play_next:
            self._player.finished()

        self.__update_timer()

    def RetrieveAlbumList(self, request: mmp_pb2.MediaData, context):
        logging.info("RetrieveAlbumList")
        alist = mmp_pb2.AlbumList()
        alist.album_list.extend([album.to_protobuf() for album in self.albums])
        return alist

    def RetrieveSongList(self, request: mmp_pb2.MediaData, context):
        logging.info("RetrieveSongList")
        response = mmp_pb2.SongList()
        album = find_album_by_id(self.albums, request.id)
        if not album:
            # TODO: add this to response
            # self.__error_result(response, 'Album does not exist')
            return response

        response.album_id = album.id
        response.song_list.extend([song.to_protobuf() for song in album.song_list])
        return response

    def Play(self, request, context):
        logging.info("Play")
        update = False
        if request.state == mmp_pb2.MediaControl.PLAY:
            assert request.song_id > 1
            album, song = find_song_by_id(self.albums, request.song_id)
            if not song:
                return error_response(f"Song with id {request.song_id} does not exist")

            logging.info("Play song")
            update = self._player.play(song)
        elif request.state == mmp_pb2.MediaControl.PAUSE:
            logging.info("Pause song")
            update = self._player.pause()
        elif request.state == mmp_pb2.MediaControl.STOP:
            logging.info("Stop song")
            update = self._player.stop()

        if update:
            self.__update_timer()

        return ok_response()

    def ChangeVolume(self, request: mmp_pb2.VolumeControl, context):
        logging.info("Change volume")
        if self._player.change_volume(request.volume_level):
            self.__update_timer()

        return empty_response()

    def ChangePosition(self, request: mmp_pb2.PositionControl, context):
        logging.info("ChangePosition")
        pos = request.position
        if 0 <= pos < 100:
            self._player.set_position(pos)
            self.__update_timer()
            return ok_response()

        return error_response("Pos not defined or not a number [0-100)")

    def Previous(self, request: mmp_pb2.PlaybackControl, context):
        logging.info("Previous")
        if self._player.play_previous():
            self.__update_timer()

        return empty_response()

    def Next(self, request, context):
        logging.info("Next")
        plays_next = self._player.play_next()
        if plays_next:
            self.__update_timer()

        return empty_response()

    def AddNext(self, request: mmp_pb2.MediaData, context):
        logging.info("AddNext")
        # TODO: Check if request is for album or song
        album, song = find_song_by_id(self.albums, request.id)
        if song:
            self.music_queue.add_next(song)
            return ok_response("Song will be played next")

        return error_response(f"Song with id {request.id} does not exist")

    def AddToQueue(self, request, context):
        logging.info("AddToQueue")
        # TODO: Check if request is for album or song
        album, song = find_song_by_id(self.albums, request.id)
        if song:
            self.music_queue.add(song)
            return ok_response("Song added to queue")

        return error_response(f"Song with id {request.id} does not exist")

    def RetrieveMMPStatus(self, request: mmp_pb2.MMPStatusRequest, context):
        logging.debug(request)
        return self._player.mmp_status()

    def RegisterMMPNotify(self, request: mmp_pb2.MMPStatusRequest, context):
        logging.debug(request)
        # when client subscribes return first status
        yield self._player.mmp_status()
        last_status_time = int(time.time())
        # keep this stream open, so we can push updates when needed
        while not self.close_streams:
            # keep checking if clients should be notified
            while self.last_update_time > last_status_time:
                last_status_time = self.last_update_time
                yield self._player.mmp_status()

    def __update_timer(self):
        logging.debug("Updated timer")
        self.last_update_time = int(time.time())
