import pandas as pd
import os
import plotly.express as px
import os
import requests
import zipfile
import shutil

DIRETORIO_BASE = './data/'


def download_ergast():
    if os.path.exists('data'):
        print("Data already downloaded.")
        return

    os.makedirs("data", exist_ok=True)
    url = 'https://ergast.com/downloads/f1db_csv.zip'

    print(f"Downloading {url}...")
    response = requests.get(url)
    with open('data/f1db_csv.zip', 'wb') as file:
        file.write(response.content)

    print("Unzipping the file...")
    with zipfile.ZipFile('data/f1db_csv.zip') as f_in:
        for file in f_in.namelist():
            with open(os.path.join('data', file), 'wb') as f_out:
                shutil.copyfileobj(f_in.open(file), f_out)

    print("Cleaning up...")
    if os.path.exists('data/f1db_csv.zip'):
        os.remove('data/f1db_csv.zip')


def load_ergast():
    data = {}
    data['drivers'] = pd.read_csv(DIRETORIO_BASE + 'drivers.csv')
    data['results'] = pd.read_csv(DIRETORIO_BASE + 'results.csv')
    data['driver_standings'] = pd.read_csv(DIRETORIO_BASE + 'driver_standings.csv')
    data['constructors'] = pd.read_csv(DIRETORIO_BASE + 'constructors.csv')
    data['constructor_results'] = pd.read_csv(DIRETORIO_BASE + 'constructor_results.csv')
    data['constructor_standings'] = pd.read_csv(DIRETORIO_BASE + 'constructor_standings.csv')
    data['races'] = pd.read_csv(DIRETORIO_BASE + 'races.csv')
    data['circuits'] = pd.read_csv(DIRETORIO_BASE + 'circuits.csv')
    data['lap_times'] = pd.read_csv(DIRETORIO_BASE + 'lap_times.csv')
    data['pit_stops'] = pd.read_csv(DIRETORIO_BASE + 'pit_stops.csv')
    data['qualifying'] = pd.read_csv(DIRETORIO_BASE + 'qualifying.csv')
    data['seasons'] = pd.read_csv(DIRETORIO_BASE + 'seasons.csv')
    data['sprint_results'] = pd.read_csv(DIRETORIO_BASE + 'sprint_results.csv')
    data['status'] = pd.read_csv(DIRETORIO_BASE + 'status.csv')
    return data