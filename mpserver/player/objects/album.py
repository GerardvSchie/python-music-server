from typing import List

from mpserver.grpc import mmp_pb2 as proto
from mpserver.player.objects.protoble import Protoble
from mpserver.player.objects.song import Song

ALBUM_ID = 1


class Album(Protoble):
    def __init__(self, title: str, location: str):
        global ALBUM_ID
        super(Album, self).__init__()
        self.id = ALBUM_ID
        ALBUM_ID += 1
        self.title = title
        self.location = location
        self.song_list: List[Song] = []

    def to_protobuf(self) -> proto.Album:
        a = proto.Album()
        a.id = self.id
        a.title = self.title
        a.song_list.extend([song.to_protobuf() for song in self.song_list])
        return a

    def __repr__(self):
        return f"Album: {self.title} (len={len(self.song_list)} id={self.id})"
