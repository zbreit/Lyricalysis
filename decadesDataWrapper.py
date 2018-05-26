import pandas as pd
from musixmatchWrapper import getLyrics, SearchParamError, CopyrightError, APILimitError
from textblob import TextBlob
from utils import avg_of, get_exception_string
import sys

# Get data about the top 100 songs in the past 6 decades from this csv
decades_of_music_df = pd.read_csv('top100ByDecade.csv', encoding='latin-1')

# Store only the artist name and title of the top 100 songs from 1950-2010
decades_of_music = {
    '1950s': decades_of_music_df[500:600][['artist_name', 'title']],
    '1960s': decades_of_music_df[400:500][['artist_name', 'title']],
    '1970s': decades_of_music_df[300:400][['artist_name', 'title']],
    # '1980s': decades_of_music_df[200:300][['artist_name', 'title']],
    # '1990s': decades_of_music_df[100:200][['artist_name', 'title']],
    # '2000s': decades_of_music_df[0:100][['artist_name', 'title']]
}

# Create a placeholder object to store all of the lyrics for top 100 songs in each decade
lyrics_by_decade = {
    '1950s': [],
    '1960s': [],
    '1970s': [],
    # '1980s': [],
    # '1990s': [],
    # '2000s': []
}

number_of_songs = 1

# For each decade, iterate over all of the songs and search for lyrics
for decade, df in decades_of_music.items():
    for index, row in df.iterrows():
        print(number_of_songs, ': ', end='')
        try:
            # Append each information about a given song to the given decade's lyrics array
            lyrics = getLyrics(row['title'], row['artist_name'])

            lyrics_by_decade[decade].append({
                'artist_name': row['artist_name'],
                'song_title': row['title'],
                'lyrics': lyrics,
                'lyrics_polarity': TextBlob(' '.join(lyrics)).sentiment.polarity
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

song_sentiments = {
    '1950s': {},
    '1960s': {},
    '1970s': {},
    # '1980s': {},
    # '1990s': {},
    # '2000s': {}
}

for key, dictionary in song_sentiments.items():
    for key in ['positive_count', 'negative_count', 'neutral_count']:
        dictionary[key] = 0

for decade, song_list in lyrics_by_decade.items():
    for song_info in song_list:
        if song_info['lyrics_polarity'] > 0:
            song_sentiments[decade]['positive_count'] += 1
        elif song_info['lyrics_polarity'] < 0:
            song_sentiments[decade]['negative_count'] += 1
        elif song_info['lyrics_polarity'] == 0:
            song_sentiments[decade]['neutral_count'] += 1   

for decade, sentiment_dict in song_sentiments.items():
    print('{}:\n\tPositive: {}\n\tNegative: {}\n\tNeutral: {}'.format(decade,
        sentiment_dict['positive_count'], sentiment_dict['negative_count'], 
        sentiment_dict['neutral_count']))
