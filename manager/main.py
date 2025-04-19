import datetime
import os
import shutil
import sys
import zipfile

import pandas as pd
import requests
from tqdm import tqdm


class Jolpica:

    BASE_URL = 'https://api.jolpi.ca/ergast/f1'

    def __requests_get(self, endpoint, season: int = None, round: int = None, limit: int = 100, offset: int = None) -> dict:
        url = f"{self.BASE_URL}"
        if season:
            url += f"/{season}"
            if round:
                url += f"/{round}"
        
        url += f"/{endpoint}"
        params = {
            'limit': limit,
            'offset': offset
        }
        response = requests.get(url, params=params)
        return response.json()

    def constructor_standing(self, season: int = None, round: int = None, limit: int = 100, offset: int = None) -> dict:
        return self.__requests_get('/constructorstandings.json', season, round, limit, offset)

    def driver_standing(self, season: int = None, round: int = None, limit: int = 100, offset: int = None) -> dict:
        return self.__requests_get('/driverstandings.json', season, round, limit, offset)
    
    def races(self, season: int = None, round: int = None, limit: int = 100, offset: int = None) -> dict:
        return self.__requests_get('/races.json', season, round, limit, offset)
    
    def drivers(self, season: int = None, round: int = None, limit: int = 100, offset: int = None) -> dict:
        return self.__requests_get('/drivers.json', season, round, limit, offset)
    
    def constructors(self, season: int = None, round: int = None, limit: int = 100, offset: int = None) -> dict:
        return self.__requests_get('/constructors.json', season, round, limit, offset)
    
    def races(self, season: int = None, round: int = None, limit: int = 100, offset: int = None) -> dict:
        return self.__requests_get('/races.json', season, round, limit, offset)
    
    def circuits(self, season: int = None, round: int = None, limit: int = 100, offset: int = None) -> dict:
        return self.__requests_get('/circuits.json', season, round, limit, offset)


def download_ergast(folder: str):
    if os.path.exists(folder):
        print("Data already downloaded.")
        return

    os.makedirs(folder, exist_ok=True)
    url = 'https://ergast.com/downloads/f1db_csv.zip'

    print(f"Downloading {url}...")
    response = requests.get(url)
    with open(os.path.join(folder, 'f1db_csv.zip'), 'wb') as file:
        file.write(response.content)

    print("Unzipping the file...")
    with zipfile.ZipFile(os.path.join(folder, 'f1db_csv.zip')) as f_in:
        for file in f_in.namelist():
            with open(os.path.join(folder, file), 'wb') as f_out:
                shutil.copyfileobj(f_in.open(file), f_out)

    print("Cleaning up...")
    if os.path.exists(os.path.join(folder, 'f1db_csv.zip')):
        os.remove(os.path.join(folder, 'f1db_csv.zip'))


def delete_folder(folder: str):
    if os.path.exists(folder):
        print(f"Deleting folder {folder}...")
        shutil.rmtree(folder)
    else:
        print(f"Folder {folder} does not exist.")


def create_database(directory: str):
    print('Creating database...')

    if os.path.exists(directory):
        print(f"Directory {directory} already exists.")
        delete_folder(directory)
    
    os.makedirs(directory, exist_ok=True)
    print(f"Directory {directory} created.")

    print("Downloading Ergast data...")
    ergast_folder = os.path.join(directory, 'ergast')
    download_ergast(ergast_folder)
    print("Ergast data downloaded.")

    print("Loading Ergast data...")
    drivers = pd.read_csv(ergast_folder + '/drivers.csv')
    driver_standings = pd.read_csv(ergast_folder + '/driver_standings.csv')
    constructors = pd.read_csv(ergast_folder + '/constructors.csv')
    constructor_standings = pd.read_csv(ergast_folder + '/constructor_standings.csv')
    races = pd.read_csv(ergast_folder + '/races.csv')
    circuits = pd.read_csv(ergast_folder + '/circuits.csv')
    print("Ergast data loaded.")

    print("Creating Jolpica data...")
    jolpica = Jolpica()

    print("Creating tables...")
    print("\tDrivers...")
    def create_drivers():
        drivers_old_map_columns = {
            'driverId': 'driverIdErgast',
            'code': 'code',
            'forename': 'givenName',
            'surname': 'familyName',
            'dob': 'dateOfBirth',
            'nationality': 'nationality',
            'url': 'url',
        }

        e_drivers = drivers[list(drivers_old_map_columns.keys())].rename(columns=drivers_old_map_columns)

        j_drivers = pd.DataFrame()
        offset = 0
        total = 1
        while j_drivers.shape[0] < total:
            print(f"Drivers: {j_drivers.shape[0]} / {total}")
            temp = jolpica.drivers(offset=offset)
            j_drivers = pd.concat([j_drivers, pd.DataFrame(temp['MRData']['DriverTable']['Drivers'])], ignore_index=True)
            total = int(temp['MRData']['total'])
            offset += 100

        j_drivers = j_drivers[['driverId', 'code', 'givenName', 'familyName', 'dateOfBirth', 'nationality', 'url']]

        e_drivers['name'] = e_drivers['givenName'] + ' ' + e_drivers['familyName']
        j_drivers['name'] = j_drivers['givenName'] + ' ' + j_drivers['familyName']

        c_drivers = pd.merge(
            e_drivers[['driverIdErgast', 'name']],
            j_drivers,
            how='outer',
            on='name',
        )
        c_drivers = c_drivers.drop(columns=['name'])
        return c_drivers
    c_drivers = create_drivers()
    
    print("\tConstructors...")
    def create_constructors():
        constructors_old_map_columns = {
            'constructorId': 'constructorIdErgast',
            'name': 'name',
        }

        e_constructors = constructors[list(constructors_old_map_columns.keys())].rename(columns=constructors_old_map_columns)

        j_constructors = pd.DataFrame()
        offset = 0
        total = 1
        while j_constructors.shape[0] < total:
            print(f"constructors: {j_constructors.shape[0]} / {total}")
            temp = jolpica.constructors(offset=offset)
            j_constructors = pd.concat([j_constructors, pd.DataFrame(temp['MRData']['ConstructorTable']['Constructors'])], ignore_index=True)
            total = int(temp['MRData']['total'])
            offset += 100

        c_constructors = pd.merge(e_constructors, j_constructors, how='outer', on='name')
        return c_constructors
    c_constructors = create_constructors()
    
    print("\tCircuits...")
    def create_circuits():
        circutis_old_map_columns = {
            'circuitId': 'circuitIdErgast',
            'name': 'circuitName',
            'location': 'locality',
            'country': 'country',
            'lat': 'lat',
            'lng': 'long',
            'url': 'url',
        }

        e_circuits = circuits[list(circutis_old_map_columns.keys())].rename(columns=circutis_old_map_columns)

        j_circuits = pd.DataFrame()
        offset = 0
        total = 1
        while j_circuits.shape[0] < total:
            print(f"circuits: {j_circuits.shape[0]} / {total}")
            temp = jolpica.circuits(offset=offset)
            j_circuits = pd.concat([j_circuits, pd.DataFrame(temp['MRData']['CircuitTable']['Circuits'])], ignore_index=True)
            total = int(temp['MRData']['total'])
            offset += 100

        c_circuits = pd.merge(
            e_circuits,
            j_circuits[['circuitName', 'circuitId']],
            on='circuitName',
            how='outer',
        )
        return c_circuits
    c_circuits = create_circuits()

    print("\tRaces...")
    def create_races():
        races_old_map_columns = {
            'raceId': 'raceIdErgast',
            'year': 'season',
            'round': 'round',
            'circuitId': 'circuitId',
            'name': 'raceName',
            'date': 'date',
            'url': 'url',
        }
        e_races = races[list(races_old_map_columns.keys())].rename(columns=races_old_map_columns)

        e_races['circuitId'] = e_races['circuitId'].map(c_circuits.set_index('circuitIdErgast')['circuitId'].to_dict())

        last_season = e_races[e_races.date == e_races.date.max()].season.iloc[0].item()

        j_races = pd.DataFrame()
        for season in range(last_season, datetime.datetime.today().year + 1):
            print(season)
            temp = jolpica.races(season=season)
            j_races = pd.concat([
                j_races,
                pd.DataFrame(temp['MRData']['RaceTable']['Races'])
            ], ignore_index=True)

        j_races['circuitId'] = j_races['Circuit'].apply(lambda x: x['circuitId'])

        j_races = j_races[['season', 'round', 'circuitId', 'raceName', 'date', 'url']]
        j_races['season'] = j_races['season'].astype(int)
        j_races['round'] = j_races['round'].astype(int)

        c_races = pd.concat([e_races, j_races], ignore_index=True).drop_duplicates(subset=['season', 'round'], keep='first').sort_values(by=['season', 'round'])
        return c_races
    c_races = create_races()

    print("\tConstructor standings...")
    def create_constructor_standings():
        constructor_standings_old_map_columns = {
            'raceId': 'raceId',
            'constructorId': 'constructorId',
            'points': 'points',
            'position': 'position',
            'wins': 'wins',
        }

        e_constructor_standings = constructor_standings[list(constructor_standings_old_map_columns.keys())].rename(columns=constructor_standings_old_map_columns)

        e_constructor_standings = pd.merge(
            e_constructor_standings.assign(raceId=e_constructor_standings.raceId.astype(float)),
            c_races[['raceIdErgast', 'season', 'round']].rename(columns={'raceIdErgast': 'raceId'}),
            how='left',
            on='raceId',
        ).drop(columns=['raceId'])

        e_constructor_standings['constructorId'] = e_constructor_standings['constructorId'].map(c_constructors.set_index('constructorIdErgast')['constructorId'].to_dict())

        missing_season_races = set([(x[0].item(), x[1].item()) for x in c_races[['season', 'round']].to_numpy()]) \
            - set([(x[0].item(), x[1].item()) for x in e_constructor_standings[['season', 'round']].to_numpy()])

        last_season = max(missing_season_races)[0]
        last_round_last_season = int(jolpica.constructor_standing(last_season)['MRData']['StandingsTable']['round'])
        missing_season_races = [x for x in missing_season_races if x <= (last_season, last_round_last_season)]
        missing_season_races = [x for x in missing_season_races if x[0] > 2000]

        j_constructors_standing = pd.DataFrame()
        for season, round in tqdm(missing_season_races):
            temp = jolpica.constructor_standing(season=season, round=round)
            temp_df = pd.DataFrame(temp['MRData']['StandingsTable']['StandingsLists'][0]['ConstructorStandings'])
            temp_df['season'] = season
            temp_df['round'] = round
            temp_df['constructorId'] = temp_df['Constructor'].apply(lambda x: x['constructorId'])
            j_constructors_standing = pd.concat([
                j_constructors_standing,
                temp_df
            ], ignore_index=True)

        j_constructors_standing = j_constructors_standing[['season', 'round', 'constructorId', 'points', 'position', 'wins']]

        c_constructor_standings = pd.concat([
            e_constructor_standings,
            j_constructors_standing
        ], ignore_index=True).drop_duplicates(subset=['season', 'round', 'constructorId'], keep='first').sort_values(by=['season', 'round'])
        return c_constructor_standings
    c_constructor_standings = create_constructor_standings()

    print("\tDriver standings...")
    def create_constructor_standings():
        driver_standings_old_map_columns = {
            'driverId': 'driverId',
            'points': 'points',
            'position': 'position',
            'wins': 'wins',

            'raceId': 'raceId',
        }

        e_driver_standings = driver_standings[list(driver_standings_old_map_columns.keys())].rename(columns=driver_standings_old_map_columns)

        e_driver_standings['driverId'] = e_driver_standings['driverId'].astype(float).map(c_drivers.dropna(subset=['driverIdErgast']).set_index('driverIdErgast')['driverId'].to_dict())

        e_driver_standings = pd.merge(
            e_driver_standings,
            c_races[['raceIdErgast', 'season', 'round']].rename(columns={'raceIdErgast': 'raceId'}),
            how='left',
        ).drop(columns=['raceId'])

        missing_season_races = set([(x[0].item(), x[1].item()) for x in c_constructor_standings[['season', 'round']].to_numpy()])

        seasons = list(set([x[0] for x in missing_season_races]))

        drivers_constructors_seasons = pd.DataFrame()
        for season in tqdm(seasons):
            temp = jolpica.driver_standing(season=season)
            temp_df = pd.DataFrame(temp['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings'])
            temp_df['season'] = season
            drivers_constructors_seasons = pd.concat([
                drivers_constructors_seasons,
                temp_df
            ], ignore_index=True)

        drivers_constructors_seasons['constructorId'] = drivers_constructors_seasons['Constructors'].apply(lambda x: x[0]['constructorId'])
        drivers_constructors_seasons['driverId'] = drivers_constructors_seasons['Driver'].apply(lambda x: x['driverId'])

        e_driver_standings = pd.merge(
            e_driver_standings,
            drivers_constructors_seasons[['driverId', 'constructorId', 'season']],
            on=['driverId', 'season'],
            how='left'
        )

        missing_season_races = set([(x[0].item(), x[1].item()) for x in c_races[['season', 'round']].to_numpy()]) \
            - set([(x[0].item(), x[1].item()) for x in e_driver_standings[['season', 'round']].to_numpy()])

        last_season = max(missing_season_races)[0]
        last_round_last_season = int(jolpica.driver_standing(last_season)['MRData']['StandingsTable']['round'])
        missing_season_races = [x for x in missing_season_races if x <= (last_season, last_round_last_season)]
        missing_season_races = [x for x in missing_season_races if x[0] > 2000]

        j_drivers_standing = pd.DataFrame()
        for season, round in tqdm(missing_season_races):
            temp = jolpica.driver_standing(season=season, round=round)
            temp_df = pd.DataFrame(temp['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings'])
            temp_df['season'] = season
            temp_df['round'] = round
            temp_df['driverId'] = temp_df['Driver'].apply(lambda x: x['driverId'])
            temp_df['constructorId'] = temp_df['Constructors'].apply(lambda x: x[0]['constructorId'])
            j_drivers_standing = pd.concat([
                j_drivers_standing,
                temp_df
            ], ignore_index=True)

        j_drivers_standing = j_drivers_standing[['season', 'round', 'driverId', 'constructorId', 'points', 'position', 'wins']]

        c_driver_standings = pd.concat([
            e_driver_standings,
            j_drivers_standing
        ], ignore_index=True).drop_duplicates(subset=['season', 'round', 'driverId'], keep='first').sort_values(by=['season', 'round'])
        return c_driver_standings
    c_driver_standings = create_constructor_standings()

    print("Saving data...")
    c_drivers.to_csv(os.path.join(directory, 'drivers.csv'), index=False)
    c_constructors.to_csv(os.path.join(directory, 'constructors.csv'), index=False)
    c_circuits.to_csv(os.path.join(directory, 'circuits.csv'), index=False)
    c_races.to_csv(os.path.join(directory, 'races.csv'), index=False)
    c_constructor_standings.to_csv(os.path.join(directory, 'constructor_standings.csv'), index=False)
    c_driver_standings.to_csv(os.path.join(directory, 'driver_standings.csv'), index=False)

    print("Data saved.")

    print("Cleaning up...")
    if os.path.exists(ergast_folder):
        shutil.rmtree(ergast_folder)
    else:
        print(f"Folder {ergast_folder} does not exist.")
    print("Cleaning up complete.")

    print("Database created.")


def update_database():
    raise NotImplementedError("Update database functionality is not implemented yet.")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python main.py <command> <directory>")
        sys.exit(1)
    
    command = sys.argv[1]
    directory = sys.argv[2]
    if command == 'create':
        create_database(directory)
    elif command == 'update':
        update_database(directory)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
