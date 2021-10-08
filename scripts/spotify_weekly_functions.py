from datetime import date, timedelta
import time
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from googletrans import Translator
import re
import sqlite3 as lite
from geopy.geocoders import Nominatim
from tqdm import tqdm
import glob
import pandas as pd

auth_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=auth_manager)

translator = Translator(service_urls=['translate.googleapis.com'])

countries = (
    "ad", "ar", "au", "at", "be",
    "bo", "br", "bg", "ca", "cl",
    "co", "cr", "cy", "cz", "dk",
    "do", "ec", "sv", "ee", "fi",
    "fr", "de", "gr", "gt", "hn",
    "hk", "hu", "id", "is", "ie", "it",
    "jp", "lv", "li", "lt", "lu", "my",
    "mt", "mx", "mc", "nl", "nz",
    "ni", "no", "pa", "py", "pe",
    "ph", "pl", "pt", "es", "sg",
    "sk", "se", "ch", "tw", "tr",
    "gb", "us", "uy")

all_markets = {
    "AD": "Andorra", "AR": "Argentina", "AU": "Australia",
    "AT": "Austria",
    "BE": "Belgium",
    "BO": "Bolivia",
    "BR": "Brazil",
    "BG": "Bulgaria",
    "CA": "Canada",
    "CL": "Chile",
    "CO": "Colombia",
    "CR": "Costa Rica",
    "CY": "Cyprus",
    "CZ": "Czech Republic",
    "DK": "Denmark",
    "DO": "Dominican Republic",
    "EC": "Ecuador",
    "SV": "El Salvador",
    "EE": "Estonia",
    "FI": "Finland",
    "FR": "France",
    "DE": "Germany",
    "GR": "Greece",
    "GT": "Guatemala",
    "HN": "Honduras",
    "HK": "Hong Kong",
    "HU": "Hungary",
    "ID": "Indonesia",
    "IS": "Iceland",
    "IE": "Republic of Ireland",
    "IT": "Italy",
    "JP": "Japan",
    "LV": "Latvia",
    "LI": "Liechtenstein",
    "LT": "Lithuania",
    "LU": "Luxembourg",
    "MY": "Malaysia",
    "MT": "Malta",
    "MX": "Mexico",
    "MC": "Monaco",
    "NL": "Netherlands",
    "NZ": "New Zealand",
    "NI": "Nicaragua",
    "NO": "Norway",
    "PA": "Panama",
    "PY": "Paraguay",
    "PE": "Peru",
    "PH": "Philippines",
    "PL": "Poland",
    "PT": "Portugal",
    "ES": "Spain",
    "SG": "Singapore",
    "SK": "Slovakia",
    "SE": "Sweden",
    "CH": "Switzerland",
    "TW": "Taiwan",
    "TR": "Turkey",
    "GB": "United Kingdom",
    "US": "United States",
    "UY": "Uruguay"
}


def df_list(data_directory):
    timestr = time.strftime("%Y%m%d")

    weekly_csv = glob.glob(data_directory + "/*weekly_{}.csv".format(timestr))
    weekly_list = []

    for weekly_file in tqdm(weekly_csv):
        tmp_weekly_df = pd.read_csv(weekly_file,
                                    skiprows=range(0, 1))
        weekly_list.append(tmp_weekly_df)

    return weekly_list


def ranking(weekly_ranking):
    weekly_ranking_list = []
    for country_weekly in tqdm(weekly_ranking):
        # Counting Artist based off number of tracks
        artist_count_weekly = country_weekly.Artist.value_counts()
        artist_count_weekly = artist_count_weekly.to_dict()
        country_weekly['Appears'] = country_weekly.Artist.map(artist_count_weekly)
        country_weekly.sort_values(['Appears'], inplace=True, ascending=False)

        # Creating string combination for amount of times Artist showed up and number of streams
        rank_weekly = country_weekly['Appears'].astype(str)
        streams_weekly = country_weekly['Streams'].astype(str)

        # Use 'max' rank in pd to pull the highest rank in the group & output files
        country_weekly['Rank'] = (rank_weekly + streams_weekly).astype(int).rank(method='max',
                                                                                 ascending=False).astype(int)
        country_weekly = country_weekly.sort_values('Rank')
        country_weekly.rename(columns={'Track Name': 'TrackName'}, inplace=True)
        country_weekly.insert(0, 'TrackID', range(0, 0 + len(country_weekly)))

        artist_genres_weekly = []
        tmp_artists_weekly = list(country_weekly.Artist)

        for artist_weekly in tmp_artists_weekly:
            translation_weekly = translator.translate("{}".format(artist_weekly))
            result_weekly = sp.search('{}'.format(translation_weekly.text), limit=1, type='artist')
            artists_w = result_weekly['artists']
            if not artists_w['items']:
                artist_genres_weekly.append('')
            else:
                artist_genres_weekly.append(artists_w['items'][0]['genres'])

        country_weekly['Artist_Genres'] = artist_genres_weekly
        weekly_ranking_list.append(country_weekly)
        time.sleep(30)

    return weekly_ranking_list


def artist_genres(weekly_genres):
    # Generating list of urls to search and create lists of song information
    # This process is done for weekly
    weekly_genres_list = []

    for country_weekly in tqdm(weekly_genres):
        weekly_song_urls = list(country_weekly.URL)
        weekly_song_ids = []

        weekly_danceability = []
        weekly_energy = []
        weekly_acousticness = []
        weekly_analysis_url = []
        weekly_duration = []
        weekly_song_id = []
        weekly_instrumentalness = []
        weekly_key = []
        weekly_liveness = []
        weekly_loundess = []
        weekly_mode = []
        weekly_speechiness = []
        weekly_tempo = []
        weekly_time_signature = []
        weekly_track_href = []
        weekly_search_type = []
        weekly_uri = []
        weekly_valence = []

        for weekly_url_id in weekly_song_urls:
            res = re.findall(r'\w+', weekly_url_id)
            weekly_song_ids.append(res[5])

        country_weekly['SongIDs'] = weekly_song_ids

        weekly_songs_attributes = []

        for w_song_id in country_weekly.SongIDs:
            w_song_info = sp.audio_features(w_song_id)
            weekly_songs_attributes.append(w_song_info)

        for weekly_attribute in weekly_songs_attributes:
            weekly_danceability.append(weekly_attribute[0]['danceability'])
            weekly_energy.append(weekly_attribute[0]['energy'])
            weekly_acousticness.append(weekly_attribute[0]['acousticness'])
            weekly_analysis_url.append(weekly_attribute[0]['analysis_url'])
            weekly_duration.append(weekly_attribute[0]['duration_ms'])
            weekly_song_id.append(weekly_attribute[0]['id'])
            weekly_instrumentalness.append(weekly_attribute[0]['instrumentalness'])
            weekly_key.append(weekly_attribute[0]['key'])
            weekly_liveness.append(weekly_attribute[0]['liveness'])
            weekly_loundess.append(weekly_attribute[0]['loudness'])
            weekly_mode.append(weekly_attribute[0]['mode'])
            weekly_speechiness.append(weekly_attribute[0]['speechiness'])
            weekly_tempo.append(weekly_attribute[0]['tempo'])
            weekly_time_signature.append(weekly_attribute[0]['time_signature'])
            weekly_track_href.append(weekly_attribute[0]['track_href'])
            weekly_search_type.append(weekly_attribute[0]['type'])
            weekly_uri.append(weekly_attribute[0]['uri'])
            weekly_valence.append(weekly_attribute[0]['valence'])

        country_weekly['Danceability'] = weekly_danceability
        country_weekly['Energy'] = weekly_energy
        country_weekly['Acousticness'] = weekly_acousticness
        country_weekly['Analysis_URL'] = weekly_analysis_url
        country_weekly['Duration_MS'] = weekly_duration
        country_weekly['Spotify_Song_ID'] = weekly_song_id
        country_weekly['Instrumentalness'] = weekly_instrumentalness
        country_weekly['Key'] = weekly_key
        country_weekly['Liveness'] = weekly_liveness
        country_weekly['Loudness'] = weekly_loundess
        country_weekly['Mode'] = weekly_mode
        country_weekly['Speechiness'] = weekly_speechiness
        country_weekly['Tempo'] = weekly_tempo
        country_weekly['Time_Signature'] = weekly_time_signature
        country_weekly['Track_Href'] = weekly_track_href
        country_weekly['Search_Type'] = weekly_search_type
        country_weekly['URI'] = weekly_uri
        country_weekly['Valence'] = weekly_valence
        weekly_genres_list.append(country_weekly)

        time.sleep(30)

    return weekly_genres_list


def geocode(weekly_geocode):
    weekly_geocode_list = []

    geolocator = Nominatim(user_agent="spotify_countries")

    for country_weekly in tqdm(weekly_geocode):
        head_tail = os.path.split(country_weekly)[1]
        country_code = head_tail.split('_', 1)[0].replace('.', '').upper()

        if country_code in all_markets:
            country_name = all_markets[country_code]
            country_weekly['Country'] = country_name

        country_weekly['gcode'] = country_weekly.full_address.apply(geolocator.geocode)

        country_weekly["Latitude"] = [g.latitude for g in country_weekly.gcode]
        country_weekly["Longitude"] = [g.latitude for g in country_weekly.gcode]

        country_weekly.drop(country_weekly.iloc[:, 0:1], inplace=True, axis=1)
        weekly_geocode_list.append(country_weekly)

        return weekly_geocode_list


def create_db(data_directory, weekly_db_files):
    conn = lite.connect(os.path.join(data_directory, 'Spotify_Rankings_Weekly.db'))
    c = conn.cursor()

    for weekly_country in weekly_db_files:
        res_weekly = re.findall(r'\w+', weekly_country)

        weekly_sql = '''CREATE TABLE {} (TrackID int PRIMARY KEY, Position int, TrackName text,
                                                Artist text, Streams int, URL float, Appears int, Rank int,
                                                SongIDs int, Danceability float, Energy float, Acousticness float, Analysis_URL text,
                                                Duration_MS int, Spotify_Song_ID int, Instrumentalness float, Key int, Liveness float,
                                                Loudness float, Mode int, Speechiness float, Tempo float,
                                                Time_Signature int, Track_Href text, Search_Type text, URI text,
                                                Valence float, Artist_Genres text, Country text, Latitude real, Longitude real)'''.format(
            res_weekly[5])
        c.execute(weekly_sql)

    conn.close()
