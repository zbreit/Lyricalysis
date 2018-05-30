import pandas as pd
from musixmatchWrapper import getLyrics, SearchParamError, CopyrightError, APILimitError
from textblob import TextBlob
from utils import avg_of, get_exception_string
import sys

# Get data about the top 100 songs in the past 6 decades from this csv
decades_of_music_df = pd.read_csv('top100ByDecade.csv', encoding='latin-1')

# Store only the artist name and title of the top 100 songs from 1950-2010
decades_of_music = {
    '1950s': {
        'dataframe': decades_of_music_df[500:600][['artist_name', 'title']],
        'lyrics': [],
        'song_sentiments': {}
    },
    '1960s': {
        'dataframe': decades_of_music_df[400:500][['artist_name', 'title']],
        'lyrics': [],
        'song_sentiments': {}
    },
    '1970s': {
        'dataframe': decades_of_music_df[300:400][['artist_name', 'title']],
        'lyrics': [],
        'song_sentiments': {}
    },
    '1980s': {
        'dataframe': decades_of_music_df[200:300][['artist_name', 'title']],
        'lyrics': [],
        'song_sentiments': {}
    },
    '1990s': {
        'dataframe': decades_of_music_df[100:200][['artist_name', 'title']],
        'lyrics': [],
        'song_sentiments': {}
    },
    '2000s': {
        'dataframe': decades_of_music_df[0:100][['artist_name', 'title']],
        'lyrics': [],
        'song_sentiments': {}
    }
}

number_of_songs = 1

# For each decade, iterate over all of the songs and search for lyrics
for decade, dictionary in decades_of_music.items():
    for index, row in dictionary['dataframe'].iterrows():
        print(number_of_songs, ': ', end='')
        try:
            # Append each information about a given song to the given decade's lyrics array
            lyrics = getLyrics(row['title'], row['artist_name'])

            decades_of_music[decade]['lyrics'].append({
                'artist_name': row['artist_name'],
                'song_title': row['title'],
                'lyrics': lyrics,
                'lyrics_polarity': TextBlob(' '.join(lyrics))
            })
            print('\'{}\' by \'{}\''.format(row['title'], row['artist_name']))
        except CopyrightError as e:
            print(get_exception_string(e))
        except SearchParamError as e:
            print(get_exception_string(e))
        except APILimitError as e:
            print(get_exception_string(e))
            exit()
        except Exception as e:
            print('\'{}\' by \'{}\' received the following error:\n{}'.format(row['title'], 
                row['artist_name'], get_exception_string(e)))
        number_of_songs += 1

for decade, dictionary in decades_of_music.items():
    for key in ['positive_count', 'negative_count', 'neutral_count']:
        dictionary['song_sentiments'][key] = 0

for decade, dictionary in decades_of_music.items():
    for song_info in song_list:
        if song_info['lyrics_polarity'] > 0:
            song_sentiments[decade]['positive_count'] += 1

for decade, polarities in song_sentiments.items():
    print('{}: {}'.format(decade, avg_of(polarities)))