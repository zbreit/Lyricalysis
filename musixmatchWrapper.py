from musixmatch import Musixmatch
from pprint import pprint
from utils import time
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

def getLyrics(song_title, artist):
    """ Returns an array containing all of the lyrics of a single song given the song title and artist name.
        If there was a malformed query, it throws a SearchParamError
        If there was a copyright issue, it throws a CopyrightError
        If there was a connection error, it throws a requests.exceptions.ConnectionError
    """
    lyric_response = musixmatch.matcher_lyrics_get(song_title, artist)
    status_code = lyric_response['message']['header']['status_code']

    if status_code == 404:
        raise SearchParamError('Could not locate the song \'{}\' by \'{}\''.format(song_title, artist))
    
    elif status_code == 401:
        raise APILimitError('Exceeded the max number of daily API calls')

    elif status_code != 200:
        exception = requests.exceptions.HTTPError("Received a status code of " +  str(status_code))
        raise exception

    elif lyric_response['message']['body']['lyrics']['restricted'] == 1:
        raise CopyrightError('The song \'{}\' by \'{}\' has restricted lyrics.'.format(song_title, artist))
    
    else:
        lyric_letters = lyric_response['message']['body']['lyrics']['lyrics_body']

    lyric_letters = stripBrandedMessage(lyric_letters)
    lyrics = lyric_letters.split()
    return lyrics

def stripBrandedMessage(lyrics):
    """ Removes the branded messaging (and any trailing numbers at the end) from the lyrics """
    if(re.search(r'\d', lyrics[:-2])):
        CHARS_IN_BRANDED_MESSAGE = 69
    else:    
        CHARS_IN_BRANDED_MESSAGE = 53
    return lyrics[:-CHARS_IN_BRANDED_MESSAGE]

"""
# Test
try:
    pprint(getLyrics('let it be', 'the beatles'))
except SearchParamError as e:
    logging.error(e)
except CopyrightError as e:
    logging.error(e)
"""
