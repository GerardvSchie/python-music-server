import vlc
import logging

from mpserver.datastructure.music_queue import MusicQueue
from mpserver.grpc import mmp_pb2
from mpserver.player.objects.event import Events
from mpserver.player.objects.song import Song
from mpserver.utils.event_firing import EventFiring


class VLCPlayer(EventFiring):
    """
        This class can play music with the vlc library it keeps track of which file it is playing.
        This class has: play, pause, etc. controls. It also manages which albums/songs there are
    """
    def __init__(self, music_queue: MusicQueue, on_finish):
        super().__init__()
        self.music_queue = music_queue
        self.v: vlc.Instance = vlc.Instance('--novideo')
        self.vlc_player: vlc.MediaPlayer = self.v.media_player_new()
        self.vlc_player.event_manager().event_attach(vlc.EventType.MediaPlayerEndReached, on_finish)

    def play(self, song: Song, add_to_queue=True) -> bool:
        if self._is_playing():
            logging.warning("Cannot play since it is already playing")
            return False

        logging.debug(f"Play: {song.title} (id={song.id} addToQueue={add_to_queue})")
        if add_to_queue:
            logging.debug("Added to queue!!")
            self.music_queue.add(song)

        try:
            logging.info(f"Before new media {song.filepath}")
            media = self.v.media_new(song.filepath)
            logging.info("Set Media")
            self.vlc_player.set_media(media)
            logging.info("Play")
            self.vlc_player.play()
            logging.info("Play VLC")
        except vlc.VLCException as e:
            logging.warning(e)
            return False
        except Exception as e:
            logging.warning(e)

        # wait for song to actual playing
        while not self.vlc_player.is_playing():
            pass

        logging.info("Playing")
        self._fire_event(Events.PLAYING)
        logging.info("Fired event")
        return True

    def play_previous(self) -> bool:
        prev_song = self.music_queue.previous()
        if not prev_song:
            logging.error("No previous song found")
            return False

        self._fire_event(Events.PLAY_PREV)
        logging.debug("Play previous song")
        return self.play(prev_song, False)

    def play_next(self):
        next_song = self.music_queue.next()
        if not next_song:
            logging.warning("No next song found")
            return False

        self._fire_event(Events.PLAY_NEXT)
        logging.debug("Play next song")
        return self.play(next_song, False)

    def finished(self):
        logging.debug("Song finished")
        self.vlc_player.set_position(1)
        self._fire_event(Events.FINISHED)
        return True

    def change_volume(self, volume: int):
        volume = clamp(int(volume), 0, 100)
        if volume == self._get_volume():
            return False

        logging.debug(f"Setting volume from {self._get_volume()} -> {volume}")
        self._set_volume(volume)
        self._fire_event(Events.VOLUME_CHANGE)
        return True

    def change_pos(self, pos):
        logging.debug("Change Position")
        # Seek to location of current playing song
        self.set_position(pos)
        if not self.vlc_player.is_playing():
            self.vlc_player.play()

        return True

    def pause(self):
        logging.debug("Pause")
        self.vlc_player.pause()
        self._fire_event(Events.PAUSING)
        return True

    def stop(self):
        logging.debug("Stop vlc")
        self.vlc_player.stop()
        self._fire_event(Events.STOPPING)
        return True

    def shutdown(self):
        logging.debug("Shutting down")
        return self.stop()

    def set_position(self, pos: float):
        # Sets the position in the song
        assert 0 <= pos <= 100, "Position not between 0 and 100"
        self.vlc_player.set_position(pos / 100)
        self._fire_event(Events.POS_CHANGE)
        return True

    def mmp_status(self):
        status = mmp_pb2.MMPStatus()
        status.state = self._get_mmp_state()
        current_song = self.music_queue.current()
        if current_song:
            status.current_song.CopyFrom(current_song.to_protobuf())

        status.volume = self._get_volume()
        status.mute = self.vlc_player.audio_get_mute()

        position = self._get_position()
        if position == -1:
            status.position = -1
        else:
            status.position = int(position * 100)

        time = self.vlc_player.get_time()
        if time == -1:
            status.elapsed_time = -1
        else:
            status.elapsed_time = int(time / 1000)

        logging.debug(f"\n{str(status)}")

        return status

    def _get_mmp_state(self):
        try:
            # get current vlc state -> replace "State." part -> to uppercase = this should match proto state
            return mmp_pb2.MMPStatus.State.Value(str(self.vlc_player.get_state()).replace('State.', '').upper())
        except ValueError:
            return mmp_pb2.MMPStatus.NOTHING_SPECIAL

    def _is_playing(self):
        return self.vlc_player.is_playing()

    def _get_volume(self):
        return self.vlc_player.audio_get_volume()

    def _set_volume(self, volume):
        self.vlc_player.audio_set_volume(volume)

    def _get_mute(self):
        return self.vlc_player.audio_get_mute()

    def _get_position(self):
        return self.vlc_player.get_position()

    def _set_position(self, position):
        self.vlc_player.set_position(position)


def clamp(value, lower_limit, upper_limit):
    return max(lower_limit, min(value, upper_limit))
