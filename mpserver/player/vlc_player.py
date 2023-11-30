import os
import vlc
import logging

from mpserver.datastructure.music_queue import MusicQueue
from mpserver.grpc import mmp_pb2
from mpserver.player.objects.event import Events
from mpserver.player.objects.song import Song
from mpserver.utils.config_parser import MusicServerConfigParser as ConfigParser
from mpserver.utils.event_firing import EventFiring


class VLCPlayer(EventFiring):
    """
        This class can play music with the vlc library it keeps track of which file it is playing.
        This class has: play, pause, etc. controls. It also manages which albums/songs there are
    """
    def __init__(self, music_queue: MusicQueue):
        super().__init__()
        self.music_queue = music_queue
        self.v: vlc.Instance = vlc.Instance('--novideo')
        self.vlc_player: vlc.MediaPlayer = self.v.media_player_new()
        self.vlc_player.event_manager().event_attach(vlc.EventType.MediaPlayerEndReached, self.__song_finished)
        self.play_file(ConfigParser.on_ready())

    def play(self, song: Song, add_to_queue=True):
        logging.debug(f"Play: {song.title} (id={song.id})")
        # This can go wrong if another program is using the file
        try:
            if add_to_queue:
                self.music_queue.latest(song)
            self.vlc_player.set_mrl(song.filepath)
            self.vlc_player.play()
            # wait for song to actual playing
            while self.vlc_player.get_state() != vlc.State.Playing:
                pass
            self._fire_event(Events.PLAYING)
        except vlc.VLCException as e:
            logging.warning(e)

    def play_previous(self):
        # Play previous song from queue
        prev_song = self.music_queue.previous()
        if not prev_song:
            logging.warning("No previous song")
            return

        logging.debug("Play previous song")
        self._fire_event(Events.PLAY_PREV)
        self.play(prev_song, False)

    def play_next(self):
        # Play next song in queue
        next_song = self.music_queue.next()
        if not next_song:
            logging.warning("No next song")
            return

        logging.debug("Play next song")
        self._fire_event(Events.PLAY_NEXT)
        self.play(next_song, False)

    def __song_finished(self, _):
        """
        Song finished listener
        This fires when song is finished
        """
        logging.debug("Song finished")
        # when song is finished play next song in the queue
        if self.music_queue.has_next():
            self.play_next()
        else:
            self.vlc_player.set_position(1)
            self._fire_event(Events.FINISHED)
            self.__update_clients()

    def change_volume(self, volume: int):
        # TODO: send confirmation that volume changed
        assert type(volume) is int, "Volume must be an int"
        new_vol = clamp(volume, 0, 100)
        if new_vol == self.vlc_player.audio_get_volume():
            return

        logging.debug(f"Setting volume from {self.vlc_player.audio_get_volume()} to {new_vol}")
        self.vlc_player.audio_set_volume(new_vol)
        self._fire_event(Events.VOLUME_CHANGE)

    def change_pos(self, pos):
        logging.debug("Change Position")
        # Seek to location of current playing song
        self.vlc_player.set_time(clamp(pos, 0, self.vlc_player.get_media().get_duration()))
        if not self.vlc_player.is_playing():
            self.vlc_player.play()

    def pause(self):
        logging.debug("Pause")
        self.vlc_player.pause()
        self._fire_event(Events.PAUSING)

    def stop(self):
        logging.debug("Stop")
        self.vlc_player.stop()
        self._fire_event(Events.STOPPING)

    def shutdown(self):
        logging.debug("Shutting down")
        self.vlc_player.stop()

    def play_file(self, file: str) -> None:
        # Play a file without interrupting the original player
        path = os.path.abspath(file)
        assert os.path.isfile(path), f"File '{file}' does not exist"

        if self.vlc_player.get_state() == vlc.State.Playing:
            return

        # create new player so it doesn't disturb the original
        player = self.v.media_player_new()
        player.audio_set_volume(self.vlc_player.audio_get_volume())
        player.set_media(self.v.media_new(file))
        player.play()

    def set_position(self, pos: float):
        # Sets the position in the song
        assert 0 <= pos <= 100, "Position not between 0 and 100"
        self.vlc_player.set_position(pos / 100)
        self._fire_event(Events.POS_CHANGE)

    def mmp_status(self):
        status = mmp_pb2.MMPStatus()
        try:
            # get current vlc state -> replace "State." part -> to uppercase = this should match proto state
            status.state = mmp_pb2.MMPStatus.State.Value(str(self.vlc_player.get_state()).replace('State.', '').upper())
        except ValueError:
            status.state = mmp_pb2.MMPStatus.NOTHING_SPECIAL

        current_song = self.music_queue.current()
        if current_song:
            status.current_song.CopyFrom(current_song.to_protobuf())

        status.volume = self.vlc_player.audio_get_volume()
        status.mute = self.vlc_player.audio_get_mute()

        position = self.vlc_player.get_position()
        if position == -1:
            status.position = -1
        else:
            status.position = int(position * 100)

        time = self.vlc_player.get_time()
        if time == -1:
            status.elapsed_time = -1
        else:
            status.elapsed_time = time / 1000

        logging.debug(f"\n{str(status)}")

        return status


def clamp(value, lower_limit, upper_limit):
    return max(lower_limit, min(value, upper_limit))
