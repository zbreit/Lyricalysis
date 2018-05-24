import pandas as pd
from musixmatchWrapper import getLyrics, SearchParamError, CopyrightError
from textblob import TextBlob

decades_of_music_df = pd.read_csv('top100ByDecade.csv', encoding='latin-1')

# Store only the artist name and title of the top 100 songs from 1950-2010
decades_of_music = {
    '1950s': decades_of_music_df[500:600][['artist_name', 'title']],
    '1960s': decades_of_music_df[400:500][['artist_name', 'title']],
    '1970s': decades_of_music_df[300:400][['artist_name', 'title']],
    '1980s': decades_of_music_df[200:300][['artist_name', 'title']],
    '1990s': decades_of_music_df[100:200][['artist_name', 'title']],
    '2000s': decades_of_music_df[0:100][['artist_name', 'title']]
}

lyrics_by_decade = {
    '1950s': [],
    '1960s': [],
    '1970s': [],
    '1980s': [],
    '1990s': [],
    '2000s': []
}

numSongs = 1

for decade, df in decades_of_music.items():
    for index, row in df.iterrows():
        print(numSongs, ': ', end='')
        try:
            [lyrics_by_decade[decade].append(lyric) for lyric in getLyrics(row['title'], row['artist_name'])]
            print(row['title'], 'by', row['artist_name'])
        except CopyrightError as e:
            print(e)
        except SearchParamError as e:
            print(e)
        except json.decoder.JSONDecodeError as e:
            print(e)
            print('Song: {} by {}'.format(row['title'], row['artist_name']))
        numSongs += 1

lyricBlobs = {}

for decade, lyrics in lyrics_by_decade.items():
    lyricBlobs[decade] = TextBlob(' '.join(lyrics))
    for sentence in lyricBlobs[decade].sentences:
        print('Sentence: {}\n\tPolarity: {}\n\n'.format(sentence, 
            sentence.sentiment.polarity))
