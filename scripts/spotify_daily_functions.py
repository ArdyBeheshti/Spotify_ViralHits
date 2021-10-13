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

    daily_csv = glob.glob(data_directory + "/*daily_{}.csv".format(timestr))
    daily_list = []

    for daily_file in tqdm(daily_csv):
        tmp_daily_df = pd.read_csv(daily_file,
                                   skiprows=range(0, 1))
        daily_list.append(tmp_daily_df)

    return daily_list


def ranking(daily_dfs):
    daily_ranking_list = []

    for country_daily in tqdm(daily_dfs):
        # Counting Artist based off number of tracks
        artist_count_daily = country_daily.Artist.value_counts()
        artist_count_daily = artist_count_daily.to_dict()
        country_daily['Appears'] = country_daily.Artist.map(artist_count_daily)
        country_daily.sort_values(['Appears'], inplace=True, ascending=False)

        # Creating string combination for amount of times Artist showed up and number of streams
        rank_daily = country_daily['Appears'].astype(str)
        streams_daily = country_daily['Streams'].astype(str)

        # Use 'max' rank in pd to pull the highest rank in the group & output files
        country_daily['Rank'] = (rank_daily + streams_daily).astype(int).rank(method='max',
                                                                              ascending=False).astype(
            int)
        country_daily = country_daily.sort_values('Rank')
        country_daily.rename(columns={'Track Name': 'TrackName'}, inplace=True)
        country_daily.insert(0, 'TrackID', range(0, 0 + len(country_daily)))

        artist_genres_daily = []
        tmp_artists_daily = list(country_daily.Artist)

        for artist_daily in tmp_artists_daily:
            translation_daily = translator.translate("{}".format(artist_daily))
            result_daily = sp.search('{}'.format(translation_daily.text), limit=1, type='artist')
            artists_d = result_daily['artists']
            if not artists_d['items']:
                artist_genres_daily.append('')
            else:
                artist_genres_daily.append(artists_d['items'][0]['genres'])

        country_daily['Artist_Genres'] = artist_genres_daily
        daily_ranking_list.append(country_daily)
        time.sleep(10)

    return daily_ranking_list


def artist_song_characteristics(daily_characteristics):
    # Generating list of urls to search and create lists of song information
    # This process is done for daily
    daily_genres_list = []

    for country_daily in tqdm(daily_characteristics):
        daily_song_urls = list(country_daily.URL)
        daily_song_ids = []

        daily_danceability = []
        daily_energy = []
        daily_acousticness = []
        daily_analysis_url = []
        daily_duration = []
        daily_song_id = []
        daily_instrumentalness = []
        daily_key = []
        daily_liveness = []
        daily_loundess = []
        daily_mode = []
        daily_speechiness = []
        daily_tempo = []
        daily_time_signature = []
        daily_track_href = []
        daily_search_type = []
        daily_uri = []
        daily_valence = []

        for daily_url_id in daily_song_urls:
            res = re.findall(r'\w+', daily_url_id)
            daily_song_ids.append(res[5])

        country_daily['SongIDs'] = daily_song_ids

        daily_songs_attributes = []

        for d_song_id in country_daily.SongIDs:
            d_song_info = sp.audio_features(d_song_id)
            daily_songs_attributes.append(d_song_info)

        for daily_attribute in daily_songs_attributes:
            daily_danceability.append(daily_attribute[0]['danceability'])
            daily_energy.append(daily_attribute[0]['energy'])
            daily_acousticness.append(daily_attribute[0]['acousticness'])
            daily_analysis_url.append(daily_attribute[0]['analysis_url'])
            daily_duration.append(daily_attribute[0]['duration_ms'])
            daily_song_id.append(daily_attribute[0]['id'])
            daily_instrumentalness.append(daily_attribute[0]['instrumentalness'])
            daily_key.append(daily_attribute[0]['key'])
            daily_liveness.append(daily_attribute[0]['liveness'])
            daily_loundess.append(daily_attribute[0]['loudness'])
            daily_mode.append(daily_attribute[0]['mode'])
            daily_speechiness.append(daily_attribute[0]['speechiness'])
            daily_tempo.append(daily_attribute[0]['tempo'])
            daily_time_signature.append(daily_attribute[0]['time_signature'])
            daily_track_href.append(daily_attribute[0]['track_href'])
            daily_search_type.append(daily_attribute[0]['type'])
            daily_uri.append(daily_attribute[0]['uri'])
            daily_valence.append(daily_attribute[0]['valence'])

        country_daily['Danceability'] = daily_danceability
        country_daily['Energy'] = daily_energy
        country_daily['Acousticness'] = daily_acousticness
        country_daily['Analysis_URL'] = daily_analysis_url
        country_daily['Duration_MS'] = daily_duration
        country_daily['Spotify_Song_ID'] = daily_song_id
        country_daily['Instrumentalness'] = daily_instrumentalness
        country_daily['Key'] = daily_key
        country_daily['Liveness'] = daily_liveness
        country_daily['Loudness'] = daily_loundess
        country_daily['Mode'] = daily_mode
        country_daily['Speechiness'] = daily_speechiness
        country_daily['Tempo'] = daily_tempo
        country_daily['Time_Signature'] = daily_time_signature
        country_daily['Track_Href'] = daily_track_href
        country_daily['Search_Type'] = daily_search_type
        country_daily['URI'] = daily_uri
        country_daily['Valence'] = daily_valence
        daily_genres_list.append(country_daily)

        time.sleep(30)

    return daily_genres_list


def geocode(daily_geocode):
    daily_geocode_list = []

    geolocator = Nominatim(user_agent="spotify_countries")

    for country_daily in tqdm(daily_geocode):
        head_tail = os.path.split(country_daily)[1]
        country_code = head_tail.split('_', 1)[0].replace('.', '').upper()

        if country_code in all_markets:
            country_name = all_markets[country_code]
            country_daily['Country'] = country_name

        # each value from city column
        # will be fetched and sent to
        # function find_geocode
        country_daily['gcode'] = country_daily['Country'].apply(geolocator.geocode)

        country_daily["Latitude"] = [g.latitude for g in country_daily.gcode]
        country_daily["Longitude"] = [g.latitude for g in country_daily.gcode]

        country_daily.drop(country_daily.iloc[:, 0:1], inplace=True, axis=1)
        daily_geocode_list.append(country_daily)

    return daily_geocode_list


def create_db(data_directory, daily_db_files):
    conn = lite.connect(os.path.join(data_directory, 'Spotify_Rankings_Daily.db'))
    c = conn.cursor()

    for daily_country in daily_db_files:
        res = re.findall(r'\w+', daily_country)
        daily_sql = '''CREATE TABLE {} (TrackID int PRIMARY KEY, Position int, TrackName text,
                                                Artist text, Streams int, URL float, Appears int, Rank int,
                                                SongIDs int, Danceability float, Energy float, Acousticness float, Analysis_URL text,
                                                Duration_MS int, Spotify_Song_ID int, Instrumentalness float, Key int, Liveness float,
                                                Loudness float, Mode int, Speechiness float, Tempo float,
                                                Time_Signature int, Track_Href text, Search_Type text, URI text,
                                                Valence float, Artist_Genres text, Country text, Latitude real, Longitude real)'''.format(
            res[5])

        c.execute(daily_sql)

        conn.commit()

    conn.close()