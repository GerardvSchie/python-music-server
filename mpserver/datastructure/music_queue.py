import logging
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
    def __init__(self, limit: int = 30):
        self._limit = limit
        self._pointer = 0
        self._queue: List[Song] = list()

    def add(self, song: Song):
        self._queue.append(song)
        if len(self) > self._limit:
            # if the queue is to big then remove the first played item
            del self._queue[0]

    def add_next(self, song: Song):
        self._queue.insert(self._pointer + 1, song)
        # if the list is to big then remove the first item in the list, which was played first
        if len(self) > self._limit:
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

    def shuffle(self):
        # TODO: return random song which hasn't played before
        # When using random it is possible an earlier track gets returned
        self._pointer = random.randrange(0, len(self))
        return self.current()

    def clear(self):
        self._queue.clear()
        self._pointer = 0

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self._queue)

    def __len__(self):
        return len(self._queue)

    def latest(self, song):
        self.add(song)
        self._pointer = len(self) - 1

    def replace_all(self, song_list: List[Song], pointer: int):
        self._queue = song_list
        if 0 < pointer < len(song_list):
            self._pointer = pointer
        else:
            self._pointer = 0
