import pandas as pd
from musixmatchWrapper import get_album_lyrics, SearchParamError, CopyrightError, APILimitError
from textblob import TextBlob
from utils import avg_of, get_exception_string
import sys
import statistics

# Grab a list of all influential rock albums
albums_df = pd.read_csv(sys.argv[1], encoding='latin-1')

polarity_list = []

def get_avg_polarity(list_of_lyrics):
    """ Returns the average polarity of all the lyrics in a given list of lyrics """
    avg_polarity = 0

    for song in list_of_lyrics:
        avg_polarity += TextBlob(' '.join(song)).sentiment.polarity
    
    if(len(list_of_lyrics) != 0):
        avg_polarity /= len(list_of_lyrics)
    else:
        raise ZeroDivisionError("Song list was empty")
    
    return avg_polarity

for index, album in albums_df.iterrows():
    artist_name = album['artist_name']
    album_name = album['album_name']

    print('{}: \'{}\' by \'{}\''.format(index + 1, album_name, artist_name), flush=True)

    try:
        song_lyric_list = get_album_lyrics(album_name, artist_name)
        polarity_list.append(get_avg_polarity(song_lyric_list))

    except CopyrightError as e:
        print(get_exception_string(e))
    except SearchParamError as e:
        print(get_exception_string(e))
    except APILimitError as e:
        print(get_exception_string(e))
        exit()
    except Exception as e:
        print(get_exception_string(e))

chi_square_counts = {
    'positive': 0,
    'negative': 0,
    'neutral': 0
}

for polarity in polarity_list:
    if polarity > 0:
        chi_square_counts['positive'] += 1
    elif polarity < 0:
        chi_square_counts['negative'] += 1
    else:
        chi_square_counts['neutral'] += 1

print('\n\nStatistcs:')
print('\tMean Polarity:', statistics.mean(polarity_list))
print('\tStandard Deviation:', statistics.stdev(polarity_list))

# Print out chi-square counts
[print('{}: {}'.format(key, counts)) for key, counts in chi_square_counts.items()]
