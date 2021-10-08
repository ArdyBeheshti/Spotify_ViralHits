import os
from scripts import spotify_daily_functions, spotify_daily_pull

timestr = time.strftime("%Y%m%d")

path = os.getcwd()
data_directory = os.path.join(path, f'data/csvs/{timestr}')

if not os.path.exists(data_directory):
    os.makedirs(data_directory + '/' + f'{timestr}')
    print(f'Made {data_directory} folder.')

spotify_daily_pull.data_pull_daily(data_directory)
print("Finished pulling daily Spotify data")

daily_dfs = spotify_daily_functions.df_list(data_directory)
print("Daily dataframe lists created")

daily_ranking_dfs = spotify_daily_functions.ranking(daily_dfs)
print("Finished ranking daily Spotify songs")

daily_generes_df = spotify_daily_functions.artist_genres(daily_ranking_dfs)
print("Finished getting genres for each artist")

daily_geocode_df = spotify_daily_functions.geocode(daily_generes_df)
print("Finished geocoding")

spotify_daily_functions.create_db(data_directory, daily_geocode_df)
print("Created database for daily songs")
print("Completed daily song functions!")
