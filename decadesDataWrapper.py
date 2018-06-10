import pandas as pd
from musixmatchWrapper import get_lyrics_by_search, SearchParamError, CopyrightError, APILimitError
from textblob import TextBlob
from utils import avg_of, get_exception_string
import sys

# Get data about the top 100 songs in the past 6 decades from this csv
decades_of_music_df = pd.read_csv('top100ByDecade.csv', encoding='latin-1')

# Store only the artist name and title of the top 100 songs from 1950-2010
decades_of_music = {
    '1950s': {},
    '1960s': {},
    '1970s': {},
    '1980s': {},
    '1990s': {},
    '2000s': {}
}

# Keeps track of which decade of songs is being selected from the data frame
slice_index = 500

# Populate each decade's dictionary with the appropriate fields
for decade, decade_info in decades_of_music.items():
    decade_info['dataframe'] = decades_of_music_df[slice_index:(slice_index + 100)][['artist_name',
        'title']]
    decade_info['song_info_list'] = []
    decade_info['song_sentiments'] = {
        'positive_count': 0,
        'negative_count': 0,
        'neutral_count': 0,
    }
    decade_info['avg_polarity'] = 0
    slice_index -= 100

current_song_number = 1

# For each decade, iterate over all of the songs and search for lyrics
for decade, decade_info in decades_of_music.items():
    for index, row in decade_info['dataframe'].iterrows():
        print('{}: \'{}\' by \'{}\' '.format(current_song_number, 
            row['title'], row['artist_name']))
        current_song_number += 1
        try:
            # Append each information about a given song to the given decade's lyrics array
            lyrics = get_lyrics_by_search(row['title'], row['artist_name'])

            decade_info['song_info_list'].append({
                'artist_name': row['artist_name'],
                'song_title': row['title'],
                'lyrics': lyrics,
                'lyrics_polarity': TextBlob(' '.join(lyrics)).sentiment.polarity
            })
        except CopyrightError as e:
            print(get_exception_string(e))
        except SearchParamError as e:
            print(get_exception_string(e))
        except APILimitError as e:
            print(get_exception_string(e))
            exit()
        except Exception as e:
            print(get_exception_string(e))

# After grabbing the lyrics, total the number of songs with positive, negative, or neutral polarities
for decade, decade_info in decades_of_music.items():
    for song_info in decade_info['song_info_list']:
        decade_info['avg_polarity'] += song_info['lyrics_polarity']
        if song_info['lyrics_polarity'] > 0:
            decade_info['song_sentiments']['positive_count'] += 1

        elif song_info['lyrics_polarity'] < 0:
            decade_info['song_sentiments']['negative_count'] += 1

        elif song_info['lyrics_polarity'] == 0:
            decade_info['song_sentiments']['neutral_count'] += 1   
    decade_info['avg_polarity'] /= len(decade_info['song_info_list'])
    print('\'{}\': \'{}\''.format(decade, decade_info['avg_polarity']))

# Print out chi-square counts for later analysis
for decade, decade_info in decades_of_music.items():
    print('{}:\n\tPositive: {}\n\tNegative: {}\n\tNeutral: {}'.format(decade,
        decade_info['song_sentiments']['positive_count'], 
        decade_info['song_sentiments']['negative_count'], 
        decade_info['song_sentiments']['neutral_count']))
