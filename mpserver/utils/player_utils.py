import glob
import os
import logging
from typing import Union, List, Tuple

from mpserver.utils.config_parser import MusicServerConfigParser as ConfigParser
from mpserver.player.objects.album import Album
from mpserver.player.objects.song import Song


def get_albums_and_songs() -> List[Album]:
    # Get albums and song from a specific folder and generates a list with dictionaries from it
    albums = _album_list_from_folder(ConfigParser.music_location())
    for album in albums:
        album.song_list = _music_list_from_folder(album.location)

    if not len(albums):
        logging.warning(f"No albums found in {ConfigParser.music_location()}")
    else:
        logging.debug(f"{len(albums)} albums found")

    return albums


def _album_list_from_folder(root_dir: str) -> List[Album]:
    # TODO: update documentation
    """ Generates a list of albums from specific directory
        every folder in the specified directory counts an album.
        A list with dictionaries like this will be returned:
        Example:
        [ {'name': "House", 'location': "/music/House", song_count: 13},
        {'name': "Rap", 'location': "/music/rap"} ]
    """
    albums = []
    if not os.path.isdir(root_dir):
        return albums

    for self_dir, _, files in os.walk(root_dir):
        # check if we are walking through same dir as root_dir
        if self_dir == root_dir:
            # if so then check if it should be an album specified in ini
            if not ConfigParser.music_location_is_album():
                continue

        location = self_dir
        song_count = 0
        # check if album is empty
        for extension in ConfigParser.allowed_extensions():
            song_count += len(glob.glob1(self_dir, "*." + extension))
        if song_count > 0 or ConfigParser.allow_empty_albums():
            name = os.path.basename(os.path.normpath(self_dir))
            albums.append(Album(name, location))
    return albums


def _music_list_from_folder(root_dir: str) -> List[Song]:
    """ returns a list with music names in the directory specified.
        see allowed_extensions in config file for allowed extensions

        Returns a list with dictionaries
        like so: [{"name":"Best Music by someone","file":"path/to/file.mp3"}]

        :param root_dir: Folder to search for music files
        :return: The list with all music names in the specified folder
    """
    music_list = []
    if os.path.isdir(root_dir):
        allow = tuple(ConfigParser.allowed_extensions())
        for music_file in os.listdir(root_dir):
            if music_file.endswith(allow):
                music_list.append(Song(os.path.splitext(music_file)[0], root_dir + os.sep + music_file))
        return music_list
    else:
        raise IOError(f"Folder '{root_dir}' does not exist!")


def find_album_by_id(albums: List[Album], album_id: int) -> Union[Album, None]:
    for album in albums:
        if album.id == album_id:
            return album

    logging.warning(f"Album with id={album_id} not found")
    return None


def find_song_by_id(albums: List[Album], song_id: int) -> Union[Tuple[Album, Song], Tuple[None, None]]:
    for album in albums:
        for song in album.song_list:
            if song.id == song_id:
                return album, song

    logging.warning(f"Song with id={song_id} not found")
    return None, None
