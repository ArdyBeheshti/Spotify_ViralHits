import os, time
from scripts import spotify_weekly_functions, spotify_weekly_pull

timestr = time.strftime("%Y%m%d")

path = os.getcwd()
data_directory = os.path.join(path, f'data/csvs/{timestr}')

if not os.path.exists(data_directory):
    os.makedirs(data_directory + '/' + f'{timestr}')
    print(f'Made {data_directory} folder.')

spotify_weekly_pull.data_pull_weekly(data_directory)
print("Finished pulling weekly Spotify data")

weekly_dfs = spotify_weekly_functions.df_list(data_directory)
print("Weekly dataframe lists created")

weekly_ranking_dfs = spotify_weekly_functions.ranking(weekly_dfs)
print("Finished ranking weekly Spotify songs")

weekly_songs_characteristics_df = spotify_weekly_functions.artist_song_characteristics(weekly_ranking_dfs)
print("Finished getting genres for each artist")

weekly_geocode_df = spotify_weekly_functions.geocode(weekly_songs_characteristics_df)
print("Finished geocoding")

spotify_weekly_functions.create_db(path, weekly_geocode_df)
print("Created database for weekly songs")
print("Completed weekly song functions!")
