from musixmatch import Musixmatch
from pprint import pprint
from utils import time
import logging
import json
import re
import sys

class SearchParamError(Exception):
    pass
        
class CopyrightError(Exception):
    pass
        
CLIENT_API_KEY = ''
with open('client_secret.json') as CONFIGS:
    CLIENT_API_KEY = json.load(CONFIGS)['musixmatch_api_key']
    
musixmatch = Musixmatch(CLIENT_API_KEY)

def getLyrics(song_title, artist):
    """ Returns an array containing all of the lyrics of a single song given the song title and artist name.
        If there was a malformed query, it throws a SearchParamError
        If there was a copyright issue, it throws a CopyrightError
    """
    try:
        lyric_response = musixmatch.matcher_lyrics_get(song_title, artist)
        print(lyric_response)
        if lyric_response['message']['body']['lyrics']['restricted'] == 1:
            raise CopyrightError('The song \'{}\' by \'{}\' has restricted lyrics.'.format(song_title, artist))
        else:
            lyric_letters = lyric_response['message']['body']['lyrics']['lyrics_body']
    except TypeError:
        raise SearchParamError('Could not locate the song \'{}\' by \'{}\''.format(song_title, artist))
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

# Test
try:
    pprint(getLyrics(sys.argv[1], sys.argv[2]))
except SearchParamError as e:
    logging.error(e)
except CopyrightError as e:
    logging.error(e)