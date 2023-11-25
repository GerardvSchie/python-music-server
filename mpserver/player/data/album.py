from typing import List

from mpserver.grpc import mmp_pb2 as proto
from mpserver.player.data.protoble import Protoble
from mpserver.player.data.song import SongModel

ALBUM_ID = 1


class AlbumModel(Protoble):
    """ Album class which is used to store album information """

    def __init__(self, title: str, location: str):
        """
        :param title:
        :param location:
        """
        global ALBUM_ID
        super(AlbumModel, self).__init__()
        self.id = ALBUM_ID
        ALBUM_ID += 1
        self.title = title
        self.location = location
        self.songlist = []  # type: List[SongModel]

    def getsong(self, song_id: int):
        """
        Gets a song from this album by ID or False if not found
        :rtype: SongModel
        """
        return self.songlist[song_id] if len(self.songlist) >= song_id > 0 else None

    def getsonglist(self) -> List[SongModel]:
        return self.songlist

    def set_song_list(self, songlist: list):
        self.songlist = songlist

    def to_protobuf(self) -> proto.Album:
        a = proto.Album()
        a.id = self.id
        a.title = self.title
        a.song_list.extend([song.to_protobuf() for song in self.songlist])
        return a
