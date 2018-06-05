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
    track_ids = get_track_ids(album_name, artist_name)

    album_lyrics = []
    for current_id in track_ids:
        try:
            album_lyrics.append(get_lyrics_by_id(current_id))
        except CopyrightError as e:
            print(get_exception_string(e))

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
    """
        Search for a given artist, returning only one result. This function 
        (perhaps simplistically) assumes that the first result will be the correct
        artist.
    """
    artist_search_response = musixmatch.artist_search(artist_name, page=0, page_size=2, 
        f_artist_id='', f_artist_mbid='')

    raise_for_status_error(artist_search_response['message']['header']['status_code'])

    return artist_search_response['message']['body']['artist_list'][0]['artist']['artist_id']

def get_album_id(album_name, artist_name):
    """ Returns the album id given its name and the name of the artist """
    artist_id = get_artist_id(artist_name)
    album_list = get_all_albums(artist_id)
    
    for album_dict in album_list:
        album = album_dict['album']
        if(album['album_release_type'] != 'Album'):
            continue
            
        if(album_name.lower() == album['album_name'].lower()):
            return album['album_id']

        # If the first word in the album titles match, prompt the user 
        # to see if it is a real match
        elif(album_name.split(' ')[0].lower() == album['album_name'].split(' ')[0].lower()):
            user_response = input('Is \'{}\' the same as \'{}\' (y/n)?'
                .format(album_name, album['album_name']))
            user_response = user_response.lower()
            if(user_response == 'y' or user_response == 'yes'):
                return album['album_id']
            else:
                continue
    
    raise SearchParamError('Could not locate the album \'{}\' by \'{}\''
            .format(album_name, artist_name))

def get_all_albums(artist_id):
    """ Returns a list containing all albums produced by an artist """
    album_response = musixmatch.artist_albums_get(artist_id, g_album_name=1, 
        page=0, page_size=100, s_release_date='dsc')

    raise_for_status_error(album_response['message']['header']['status_code'])
    return album_response['message']['body']['album_list']

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
        raise SearchParamError('Could not locate the song \'{}\' by \'{}\''
            .format(song_title, artist))
    
    elif status_code == 401:
        raise APILimitError('Exceeded the max number of daily API calls')

    elif status_code != 200:
        raise requests.exceptions.HTTPError('Received a status code of ' +  str(status_code))


# Test
try:
    pprint(get_album_lyrics('Homework', 'Daft Punk'))
except SearchParamError as e:
    logging.error(get_exception_string(e))
except CopyrightError as e:
    logging.error(get_exception_string(e))
except Exception as e:
    print(get_exception_string(e))
