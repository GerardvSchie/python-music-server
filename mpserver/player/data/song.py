from tinytag import TinyTag

from mpserver.grpc import mmp_pb2 as proto
from mpserver.player.data.protoble import Protoble

SONG_ID = 1


class SongModel(Protoble):
    """ A song model which is used to store song information """

    def __init__(self, title: str, filepath: str):
        global SONG_ID
        super(SongModel, self).__init__()
        self.id = SONG_ID
        SONG_ID += 1
        self.title = title
        self.filepath = filepath
        # This operation can go wrong when another program is using the filepath
        try:
            self._tags = TinyTag.get(self.filepath, False, True)
            self.duration = round(self._tags.duration)
        except PermissionError as e:
            self.duration = None
            print(e)

    def to_protobuf(self) -> proto.Song:
        s = proto.Song()
        s.id = self.id
        s.title = self.title
        s.duration = self.duration
        return s
