import threading
import time
import unittest
import mpserver.utils.logger as logger
import logging
import vlc

from mpserver.player.objects.song import Song
from mpserver.utils.config_parser import MusicServerConfigParser as ConfigParser

from mpserver.datastructure.music_queue import MusicQueue
from mpserver.player.vlc_player import VLCPlayer

finish = 0


# TODO: this test case needs improvement

def SongFinished(event):
    global finish
    print("FINISHED EVENT")
    finish = 1


class VLCTests(unittest.TestCase):
    sample_file = r'D:\Music\ABBA\Abba\ABBA - I Do, I Do, I Do, I Do, I Do.mp3'
    connected_file = r'C:\Users\gerard\MegaDrive\Documents\GitRepos\Python\python-music-server\data\sound\connected.mp3'

    def setUp(self):
        self.music_queue = MusicQueue()
        self.player: VLCPlayer = VLCPlayer(self.music_queue, self.__on_finish)
        self.player.change_volume(80)
        logger.initialize()

    def __on_finish(self, _):
        self.__set_media()
        print("finished")

    # def test_can_play_file(self):
    #     self.player.play_file(ConfigParser.on_connected())
    #     self.assertEqual(self.player.vlc_player.is_playing(), 0)
    #
    # def test_setting_volume(self):
    #     self.player.play(Song("test", self.sample_file), True)
    #     self.assertEqual(self.player.vlc_player.is_playing(), 1)
    #     volume = 10
    #     self.player.change_volume(volume)
    #     while self.player.vlc_player.get_state() == vlc.State.Playing:
    #         if volume > 100:
    #             break
    #
    #         volume += 2
    #         # vlc.MediaPlayer.audio_set_volume returns 0 if success, -1 otherwise
    #         self.player.change_volume(volume)
    #         # self.assertEqual(self.player.vlc_player.audio_get_volume(), volume, "Could not set vlc audio!")
    #         print("Volume set to: " + str(volume))
    #         time.sleep(0.05)

    # def test_play_file_when_already_playing(self):
    #     print("Override already playing media with new media")
    #     for i in range(4):
    #         self.player.play(Song(str(i), self.connected_file), True)
    #     time.sleep(2)

    def test_queue_song(self):
        self.player.play(Song("Sample", self.sample_file))
        # self.player.music_queue.add(Song("Connected", self.connected_file))
        self.player._set_position(0.97)
        # time.sleep(1)
        # self.__set_media()
        # time.sleep(1)
        # thread = threading.Thread(self.__set_media())
        # thread.start()
        time.sleep(8)

    def __set_media(self):
        logging.debug("Before set media")
        self.player.vlc_player.set_mrl(self.connected_file)
        logging.debug("Before play")
        self.player.vlc_player.play()
        logging.debug("after play")

    # def test_stream_mixcloud(self):
    #     url = 'http://stream6.mixcloud.com/secure/c/m4a/64/4/e/3/5/b074-a7ef-4da5-a2cf-a390da945cbb.m4a?sig' \
    #           '=xlsqXNRipncHPvbxNMMnfQ'
    #     self.player.play(Song("IDK", url), True)
    #     print('length: {}'.format(self.player.vlc_player.get_length()))
    #     i = 0
    #     while i < 30:
    #         print('time: {}'.format(self.player.vlc_player.get_time()))
    #         if i == 10:
    #             # test seeking in stream
    #             self.player.set_position(0.2)
    #         time.sleep(1)
    #         i += 1

    # def test_get_meta_data(self):
    #     self.player.set_mrl(self.samplefile)
    #     m = self.player.get_media()
    #     m.parse()  # Synchronous parse of the stream
    #     print('parsed')
    #     rating = m.get_meta(vlc.Meta.Rating)
    #     artwork_url = m.get_meta(vlc.Meta.ArtworkURL)  # type: str
    #     print(str(datetime.timedelta(seconds=m.get_duration() / 1000)))
    #     print(str(type(rating)) + ' - ' + str(rating))
    #     print(str(type(artwork_url)) + ' - ' + str(artwork_url))
    #     if artwork_url is not None:
    #         try:
    #             import PIL.Image
    #             img = PIL.Image.open(artwork_url.replace('file:///', ''))
    #             img.show()
    #         except ImportError:
    #             print('can\'t show image')


if __name__ == '__main__':
    unittest.main()
