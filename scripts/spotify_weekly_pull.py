from selenium.common.exceptions import NoSuchElementException
import undetected_chromedriver.v2 as uc
from datetime import date, timedelta
import time
import shutil
import glob
from pathlib import Path
import os
from tqdm import tqdm

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


def data_pull_weekly(csv_directory):
    options = uc.ChromeOptions()
    driver = uc.Chrome(options=options)

    # if not os.path.exists(csv_directory):
    #     os.makedirs(csv_directory)
    #     print(f'Made {csv_directory} folder.')

    for country in tqdm(countries):
        driver.get('https://spotifycharts.com/regional/{}/weekly/latest'.format(country))

        try:
            link_download_weekly = driver.find_element_by_link_text('DOWNLOAD TO CSV')
            set1 = link_download_weekly
            set1.click()
        except NoSuchElementException:
            continue

        time.sleep(5)

        timestr = time.strftime("%Y%m%d")

        downloads_path = str(Path.home() / "Downloads")
        os.chdir(downloads_path)

        for file in glob.glob("*weekly-latest.csv"):
            shutil.move(file, csv_directory)

        os.chdir(csv_directory)
        os.rename('regional-{}-weekly-latest.csv'.format(country), "{}_top_200_weekly_{}.csv".format(country, timestr))

    driver.quit()
