import logging
from tinytag import TinyTag

from mpserver.grpc import mmp_pb2 as proto
from mpserver.player.objects.protoble import Protoble

SONG_ID = 1


class Song(Protoble):
    def __init__(self, title: str, filepath: str):
        global SONG_ID
        super(Song, self).__init__()
        self.id = SONG_ID
        SONG_ID += 1
        self.title = title
        self.filepath = filepath
        try:
            # This operation can go wrong when another program is using the filepath
            self._tags = TinyTag.get(self.filepath, False, True)
        except PermissionError as e:
            logging.warning(e)
        self.duration = round(self._tags.duration) if self._tags else None

    def to_protobuf(self) -> proto.Song:
        s = proto.Song()
        s.id = self.id
        s.title = self.title
        s.duration = self.duration
        return s

    def __repr__(self):
        return f"Song: {self.title} (id={self.id})"
