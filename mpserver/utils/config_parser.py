import os
from configparser import ConfigParser

# Get configuration for the application
config_file = os.path.abspath('config.ini')
assert os.path.exists(config_file), f"Path {config_file} does not exist"

config = ConfigParser()
config.read(config_file)


class MusicServerConfigParser:
    @staticmethod
    def port():
        return config.getint("musicserver", "port", fallback=1010)

    @staticmethod
    def max_connections():
        return config.getint("musicserver", "max_connections", fallback=10)

    @staticmethod
    def sound_volume():
        return config.getint("musicplayer", "start_volume", fallback=40)

    @staticmethod
    def event_volume():
        return config.getint("musicplayer", "event_volume", fallback=80)

    @staticmethod
    def music_location():
        return config.get("musicplayer", "musiclocation", fallback="D:/Music")

    @staticmethod
    def allow_empty_albums():
        return config.getboolean("musicplayer", "allow_empty_albums", fallback=False)

    @staticmethod
    def music_location_is_album():
        return config.get("musicplayer", "musiclocation_is_album", fallback=True)

    @staticmethod
    def allowed_extensions():
        return set(config.get("musicplayer", "allowed_extensions", fallback="mp3,wav").split(','))

    @staticmethod
    def on_connected():
        return config.get("musicplayer/events", "onconnected", fallback="../data/sound/connected.mp3").replace('\\', '/')

    @staticmethod
    def on_ready():
        return config.get("musicplayer/events", "onready", fallback="../data/sound/ready.mp3").replace('\\', '/')

    @staticmethod
    def download_location():
        return config.get("mediadownloader", "download_location", fallback="{{album}}/%(title)s.%(ext)s")
