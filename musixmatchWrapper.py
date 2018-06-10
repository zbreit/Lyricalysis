from musixmatch import Musixmatch
from pprint import pprint
from utils import time, get_exception_string
import logging
import json
import re
import sys
import requests

# Define our own types of musixmatch exceptions
class SearchParamError(Exception):
    pass

class CopyrightError(Exception):
    pass

class APILimitError(Exception):
    pass
        
# Grab the API key from a local 'client_secret.json' file
CLIENT_API_KEY = ''
with open('client_secret.json') as CONFIGS:
    CLIENT_API_KEY = json.load(CONFIGS)['musixmatch_api_key']

# Construct an object of the Musixmatch class with the given API key
musixmatch = Musixmatch(CLIENT_API_KEY)

def get_lyrics_by_search(song_title, artist_name):
    """ Returns an array containing the lyrics of a single song given the song title and artist. """
    lyric_response = musixmatch.matcher_lyrics_get(song_title, artist_name)
    
    return get_lyrics_from_response(lyric_response)

def get_lyrics_by_id(song_id):
    """ Returns an array containing the lyrics of a single song given the musixmatch song id """
    lyric_response = musixmatch.track_lyrics_get(song_id)

    return get_lyrics_from_response(lyric_response)

def get_lyrics_from_response(song_response):
    """ Given a song response from a musixmatch API request, return an array containing that songs lyrics """
    raise_for_status_error(song_response['message']['header']['status_code'])

    if song_response['message']['body']['lyrics']['restricted'] == 1:
        raise CopyrightError('The specified song has restricted lyrics.')
    
    else:
        lyric_letters = song_response['message']['body']['lyrics']['lyrics_body']

    lyric_letters = strip_branded_message(lyric_letters)
    lyrics = lyric_letters.split()
    return lyrics

def get_album_lyrics(album_name, artist_name):
    """ Returns the song lyrics for all songs on an album given the album name and artist name """
    track_ids = get_track_ids(album_name, artist_name)

    album_lyrics = []
    
    for current_id in track_ids:
        try:
            album_lyrics.append(get_lyrics_by_id(current_id))
        except CopyrightError as e:
            print(get_exception_string(e))

    if len(album_lyrics) == 0:
        raise CopyrightError("The entire album is restricted")

    return album_lyrics

def get_track_ids(album_name, artist_name):
    """ Returns an array containing all the song ids given the album title and artist. """
    album_id = get_album_id(album_name, artist_name)
    tracks_response = musixmatch.album_tracks_get(album_id, page=0, page_size=35, album_mbid='')
    
    raise_for_status_error(tracks_response['message']['header']['status_code'])

    id_list = []
    for track in tracks_response['message']['body']['track_list']:
        id_list.append(track['track']['track_id'])

    return id_list

def get_artist_id(artist_name):
    """ Returns the musixmatch id of an artist """
    artist_search_response = musixmatch.artist_search(artist_name, page=0, page_size=10, 
        f_artist_id='', f_artist_mbid='')

    raise_for_status_error(artist_search_response['message']['header']['status_code'])

    for artist_dict in artist_search_response['message']['body']['artist_list']:
        artist = artist_dict['artist']

        if(is_exact_match(artist_name, artist['artist_name'])):
            return artist['artist_id']

        elif(is_fuzzy_match(artist_name, artist['artist_name'])):
            return artist['artist_id']

    # If no match can be found, raise an error
    raise SearchParamError("Artist not found.")

def is_exact_match(album1_title, album2_title):
    """ Returns true if the lowercase version of the provided album titles are equal """
    if get_cleansed_string(album1_title) == get_cleansed_string(album2_title):
        return True
    elif is_remaster(album1_title, album2_title) or is_edition(album1_title, album2_title):
        return True
    else:
        return False

def is_fuzzy_match(album1_title, album2_title):
    """ Returns true if there is a partial match between two album titles and the user agrees """
    # If album2_title is just album1_title plus a space, a character that isn't a letter or 
    # '&' or '/' or '-', and any number of other characters, prompt the user for a match
    if re.match(album1_title + ' [^\w&/-].+', album2_title) is not None:
        if prompt_user_match(album1_title, album2_title):
            return True
    return False

def is_remaster(album1_title, album2_title):
    """ Returns true album2 is just a remaster of album1 """
    return re.match(album1_title + ' (\[|\()(R|r)emaster(ed)?(\)|\])', album2_title) is not None

def is_edition(album1_title, album2_title):
    """ Returns true album2 is just another edition of album1 """
    return re.match(album1_title + ' (\[|\().+(E|e)dition(\)|\])', album2_title) is not None
 
def get_cleansed_string(str1):
    """ Return a string without special characters """
    EXCLUDE_LIST = ['"', '\'', '’', ',']

    # Remove all special characters from a given string
    for char in EXCLUDE_LIST:
        str1 = str1.replace(char, '')

    return str1.lower()

def get_album_id(album_name, artist_name):
    """ Returns the album id given its name and the name of the artist """
    artist_id = get_artist_id(artist_name)
    album_list = get_all_albums(artist_id)

    # Look through the albums for an exact match. 
    # If there's a partial match, prompt the user to confirm
    for album_dict in album_list:
        album = album_dict['album']

        # Remove any non-albums from the list
        if album['album_release_type'] != 'Album':
            continue
            
        if is_exact_match(album_name, album['album_name']):
            return album['album_id']

        elif is_fuzzy_match(album_name, album['album_name']):
            return album['album_id']
    
    # If no matching album can be found, raise an error
    raise SearchParamError('Could not locate the album.')

def prompt_user_match(val1, val2):
    """ Returns true if the user thinks that two provided values are equivalent """
    user_response = input('\tIs \'{}\' the same as \'{}\' (y/n)? '.format(val1, val2))
    user_response = user_response.lower()

    return user_response == 'y' or user_response == 'yes'

def get_all_albums(artist_id):
    """ Returns a list containing all albums produced by an artist """
    page_num = 0
    retreived_all_albums = False
    album_list = []

    while not retreived_all_albums:
        album_response = musixmatch.artist_albums_get(artist_id, g_album_name=1, 
            page=page_num, page_size=100, s_release_date='dsc')

        raise_for_status_error(album_response['message']['header']['status_code'])

        album_list += album_response['message']['body']['album_list']

        page_num += 1

        if album_response['message']['header']['available'] < len(album_list):
            retreived_all_albums = True

    return album_list

def strip_branded_message(lyrics):
    """ Removes the branded messaging (and any trailing numbers at the end) from the lyrics """
    if(re.search(r'\d', lyrics[:-2])):
        CHARS_IN_BRANDED_MESSAGE = 69
    else:    
        CHARS_IN_BRANDED_MESSAGE = 53
    return lyrics[:-CHARS_IN_BRANDED_MESSAGE]

def raise_for_status_error(status_code):
    """ Raises different types of exceptions depending on the status code from the musixmatch api 
        If there was a malformed query, it throws a SearchParamError
        If there was a copyright issue, it throws a CopyrightError
        If there was a connection error, it throws a requests.exceptions.ConnectionError
    """
    if status_code == 404:
        raise SearchParamError('Could not locate the given song')
    
    elif status_code == 401:
        raise APILimitError('Exceeded the max number of daily API calls')

    elif status_code != 200:
        raise requests.exceptions.HTTPError('Received a status code of ' +  str(status_code))

"""
# Test
try:
    pprint(get_album_lyrics('Shawn Mendes', 'Shawn Mendes'))
except SearchParamError as e:
    logging.error(get_exception_string(e))
except CopyrightError as e:
    logging.error(get_exception_string(e))
except Exception as e:
    print(get_exception_string(e))
"""