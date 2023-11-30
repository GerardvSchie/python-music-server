import random
from typing import List, Union

from mpserver.player.objects.song import Song


class MusicQueue:
    """
    A music queue which acts like every other MusicQueue
    It keeps a pointer to the current song

    Attributes:
        _pointer    Points to the current index of the queue
    """
    def __init__(self, songs=None, limit: int = 30):
        self._limit = limit
        self._pointer = 0

        if not songs:
            songs = list()
        assert type(songs) is list, "Songs must be a list"
        self._queue: List[Song] = songs

    def add(self, song):
        self._queue.append(song)
        if self.size() > self._limit:
            # if the queue is to big then remove the first played item
            del self._queue[0]

    def add_next(self, song):
        self._queue.insert(self._pointer + 1, song)
        # if the list is to big then remove the first item in the list, which was played first
        if self.size() > self._limit:
            del self._queue[0]

    def next(self) -> Union[Song, None]:
        if self._pointer + 1 < len(self._queue):
            self._pointer += 1
            return self.current()
        return None

    def has_next(self) -> bool:
        if self._pointer + 1 < len(self._queue):
            return True
        return False

    def previous(self) -> Union[Song, None]:
        if self._pointer - 1 >= 0:
            self._pointer -= 1
            return self.current()
        return None

    def has_previous(self) -> bool:
        if self._pointer - 1 >= 0:
            return True
        return False

    def current(self) -> Union[Song, None]:
        if len(self._queue) > 0:
            return self._queue[self._pointer]
        return None

    def size(self) -> int:
        return len(self._queue)

    def shuffle(self):
        # TODO: return random song which hasn't played before
        # When using random it is possible an earlier track gets returned
        self._pointer = random.randrange(0, len(self._queue))
        return self.current()

    def clear(self):
        self._queue.clear()
        self._pointer = 0

    def __repr__(self):
        return str(self._queue)

    def latest(self, song):
        self.add(song)
        self._pointer = len(self._queue) - 1

    def replace_all(self, songlist: List[Song], pointer: int):
        self._queue = songlist
        if 0 < pointer < len(songlist):
            self._pointer = pointer
        else:
            self._pointer = 0
