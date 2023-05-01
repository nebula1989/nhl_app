import os
import sys
import time
from pprint import pprint

from datetime import date, timedelta, datetime
import requests
import json

TODAYS_DATE = date.today()

# creates a cache directory if not one already
CACHE_DIR = 'NHL_APP/cache/'
if not os.path.exists(f'{CACHE_DIR}'):
    os.mkdir(f'{CACHE_DIR}')


def get_team_names(display_data=False):
    """
    Fetches team data from NHL api if not already in cache.
    :param: show_team_names if set to True, it will display the teams in the terminal
    :return: JSON file of NHL team data
    """

    data = fetch_data(update=False, json_cache=f'{CACHE_DIR}teams.json',
                      url='https://statsapi.web.nhl.com/api/v1/teams')

    if display_data:
        for team in data['teams']:
            print(team['name'])


def get_team_venue_names(display_data=False):
    """
    Fetches team data and creates a json file of team abbreviations and their venues.
    If no cache is found, it will reobtain the teams data and create a new json file abbreviations and venues.
    :param: display_data
    :return: a JSON file of team abbreviations and their home venues.
    """
    json_cache = 'teams_venues.json'

    try:
        with open(f'{CACHE_DIR}{json_cache}') as data:
            print(f"Fetched {json_cache} from Local cache")
            json_data = json.load(data)

        if display_data:
            pprint(json_data)

    except FileNotFoundError:
        data = fetch_data(update=False, json_cache=f'{CACHE_DIR}teams.json',
                          url='https://statsapi.web.nhl.com/api/v1/teams')

        data_length = len(data['teams'])

        team_and_venue = dict()

        for team in range(0, data_length):
            team_and_venue[data['teams'][team]['abbreviation']] = data['teams'][team]['venue']['name']

        team_venue_dict = {'team_venue': team_and_venue}

        create_json_file(json_cache, team_venue_dict)


def create_team_id_dict():
    """
    Creates a dictionary of team names and their nhl assigned IDs
    :return: a JSON file of ID as keys and team names as values
    """
    team_id_dict = dict()
    data = fetch_data(update=False, json_cache=f'{CACHE_DIR}teams.json',
                      url='https://statsapi.web.nhl.com/api/v1/teams')

    # grabs the data it needs and creates a custom dictionary
    for team_id in range(len(data['teams'])):
        team_id_dict[data['teams'][team_id]['id']] = data['teams'][team_id]['abbreviation']

    # sends the dictionary to the create json file function to be converted to a json file and stashed in the cache
    create_json_file('team_id.json', team_id_dict)


def team_id_lookup(id_or_abbreviation):
    """
    Matches a team name or a team ID or team name abbreviation with its value or key respectively
    :param id_or_abbreviation: the name or ID which has been entered by the user in the command line. ex 'python main.py id_lookup 16' would return 'CHI' and vice versa
    :return: the key (team ID) or value (team name)
    """

    with open(f'{CACHE_DIR}team_id.json') as json_file:
        try:
            if not id_or_abbreviation.isdigit():
                data_dict = json.load(json_file)
                key_list = list(data_dict.keys())
                val_list = list(data_dict.values())

                position = val_list.index(id_or_abbreviation.upper())

                print(key_list[position])

                return key_list[position]

            elif id_or_abbreviation.isdigit():
                data_dict = json.load(json_file)
                key_list = list(data_dict.keys())
                val_list = list(data_dict.values())

                value = key_list.index(id_or_abbreviation)

                print(val_list[value])

                return val_list[value]

        except ValueError:
            print("No match")
            exit()

    json_file.close()


def create_team_roster_json(team_abbreviation, display_data=False):
    ROSTER_DIR = 'rosters/'
    if not os.path.exists(f'{CACHE_DIR}{ROSTER_DIR}'):
        os.mkdir(f'{CACHE_DIR}{ROSTER_DIR}')

    data = fetch_data(update=False, json_cache=f'{CACHE_DIR}{ROSTER_DIR}{team_abbreviation}_roster.json',
                      url=f'https://statsapi.web.nhl.com/api/v1/teams/{team_id_lookup(team_abbreviation)}/roster')

    if display_data:
        for player in data['roster']:
            print(f"#{player['jerseyNumber']} {player['position']['name']} {player['person']['fullName']} ")


def fetch_data(*, update: bool = False, json_cache: str, url: str):
    '''
    Pulls data from an api address if the cached result does not exist already
    :param update:
    :param json_cache:
    :param url:
    :return:
    '''
    if update:
        json_data = None
    else:
        try:
            with open(json_cache, 'r') as file:
                json_data = json.load(file)
                # print('Fetched data from local cache.')
        except (FileNotFoundError, json.JSONDecodeError) as e:
            # print(f'No Local cache found... {e}')
            json_data = None

    if not json_data:
        # print('Fetching new json data... (Creating local cache)')
        json_data = requests.get(url).json()
        with open(json_cache, 'w') as file:
            json.dump(json_data, file, indent=4)

    return json_data


def create_json_file(json_cache, json_data):
    '''
    Creates json files from custom or filtered data
    :param json_cache:
    :param json_data:
    :return:
    '''
    with open(f'{CACHE_DIR}{json_cache}', 'w') as file:
        json.dump(json_data, file)


def games_today(display_data=True):
    """
    Fetches NHL schedule data and shows the games today and current scores
    :param display_data:
    :return: None
    """
    todays_date = date.today()
    data = fetch_data(update=True, json_cache=f'{CACHE_DIR}games_today.json',
                      url=f'https://statsapi.web.nhl.com/api/v1/schedule/?startDate{todays_date}&endDate={todays_date}')

    if display_data:
        for game in data['dates'][0]['games']:
            # display away team vs home team and current score
            print(
                f"GAME ID: {game['gamePk']}\n"
                f"{game['teams']['away']['team']['name']} {game['teams']['away']['score']} VS {game['teams']['home']['team']['name']} {game['teams']['home']['score']}\n")

    return (
        f"GAME ID: {game['gamePk']}\n"
        f"{game['teams']['away']['team']['name']} {game['teams']['away']['score']} VS {game['teams']['home']['team']['name']} {game['teams']['home']['score']}\n")


def game_id_to_headline_message(game_id):
    todays_date = date.today()
    data = fetch_data(update=True, json_cache=f'{CACHE_DIR}games_today.json',
                      url=f'https://statsapi.web.nhl.com/api/v1/schedule/?startDate{todays_date}&endDate={todays_date}')

    for game in data['dates'][0]['games']:
        if int(game_id) == game['gamePk']:
            return (
                f"{game['teams']['away']['team']['name']} {game['teams']['away']['score']} VS {game['teams']['home']['team']['name']} {game['teams']['home']['score']}"
            )


def get_todays_game_ids():
    data = fetch_data(update=True, json_cache=f'{CACHE_DIR}games_today.json',
                      url=f'https://statsapi.web.nhl.com/api/v1/schedule/?startDate{TODAYS_DATE}&endDate={TODAYS_DATE}')

    list_of_game_ids = []

    for game_id in data['dates'][0]['games']:
        list_of_game_ids.append(game_id['gamePk'])

    return list_of_game_ids


def game_plays_report(game_id, period):
    """
    shows every play of a game
    :param game_id:
    :param period:
    :return:
    """

    # If there is no game feed directory, create one to store the cache files
    FEED_DIR = 'game_plays/'
    if not os.path.exists(f'{CACHE_DIR}{FEED_DIR}'):
        os.mkdir(f'{CACHE_DIR}{FEED_DIR}')

    data = fetch_data(update=True, json_cache=f'{CACHE_DIR}{FEED_DIR}{game_id}_P{period}_plays.json',
                      url=f'https://statsapi.web.nhl.com/api/v1/game/{game_id}/feed/live')

    if data['gameData']['status']['detailedState'] == "Pre-Game":
        print('In Pre Game')
        quit()

    else:
        list_of_events = data['liveData']['plays']['allPlays']

        # Loop through the api data forwards
        '''
        for event in range(len(list_of_events)):
        '''
        # Loop through the api data backwards
        for event in reversed(range(len(list_of_events))):
            if period == 'ALL':
                print(
                    f"{list_of_events[event]['result']['event']} ({list_of_events[event]['about']['ordinalNum']} P, {list_of_events[event]['about']['periodTimeRemaining']}): {list_of_events[event]['result']['description']}, @ {list_of_events[event]['about']['dateTime'][11:19]}")
            elif period == '1':
                if list_of_events[event]['about']['period'] == 1:
                    print(
                        f"{list_of_events[event]['result']['event']} ({list_of_events[event]['about']['ordinalNum']} P, {list_of_events[event]['about']['periodTimeRemaining']}): {list_of_events[event]['result']['description']}, @ {list_of_events[event]['about']['dateTime'][11:19]}")

            elif period == '2':
                if list_of_events[event]['about']['period'] == 2:
                    print(
                        f"{list_of_events[event]['result']['event']} ({list_of_events[event]['about']['ordinalNum']} P, {list_of_events[event]['about']['periodTimeRemaining']}): {list_of_events[event]['result']['description']}, @ {list_of_events[event]['about']['dateTime'][11:19]}")

            elif period == '3':
                if list_of_events[event]['about']['period'] == 3:
                    print(
                        f"{list_of_events[event]['result']['event']} ({list_of_events[event]['about']['ordinalNum']} P, {list_of_events[event]['about']['periodTimeRemaining']}): {list_of_events[event]['result']['description']}, @ {list_of_events[event]['about']['dateTime'][11:19]}")
            else:
                print(
                    "You must enter in a game id and a period.  Ex 'python main.py ticker 2022030135 1' would give you the first period plays of period 1")
                break


def game_ending_time(game_id):
    data = fetch_data(update=False, json_cache=f'{CACHE_DIR}games_today.json',
                      url=f'https://statsapi.web.nhl.com/api/v1/schedule/?startDate{TODAYS_DATE}&endDate={TODAYS_DATE}')

    games_data = data['dates'][0]['games']
    for game in games_data:
        if str(game['gamePk']) == game_id:
            time_data = game['gameDate']
            format_data = "%Y-%m-%dT%H:%M:%SZ"
            date_obj = datetime.strptime(time_data, format_data)
            ending_time = date_obj + timedelta(hours=4)

            print(ending_time)
            return ending_time


def live_ticker(game_id):
    FEED_DIR = 'live_feeds/'

    dir_path = f"{CACHE_DIR}{FEED_DIR}"

    if not os.path.exists(f'{dir_path}'):
        os.mkdir(f'{dir_path}')

    recently_ticked_play = []
    ticks = 0

    # while current time is less than game start time plus 4 hours
    #while datetime.now() < game_ending_time(game_id):
    while True:
        headline_msg = game_id_to_headline_message(game_id)
        print(f"We are watching {headline_msg}", end="")
        # Time stuff
        NOW = datetime.now() + timedelta(hours=7)
        now_str = str(NOW)
        TIMECODE = now_str[11:19]

        # get the latest json response
        data = fetch_data(update=True, json_cache=f'{dir_path}{game_id}_feed.json',
                          url=f'https://statsapi.web.nhl.com/api/v1/game/{game_id}/feed/live')

        all_plays = data['liveData']['plays']['allPlays']
        latest_play = f"{all_plays[len(all_plays) - 1]['result']['event'].upper()}, {all_plays[len(all_plays) - 1]['about']['ordinalNum']} P {all_plays[len(all_plays) - 1]['about']['periodTimeRemaining']}, {all_plays[len(all_plays) - 1]['result']['description']}, @ {all_plays[len(all_plays) - 1]['about']['dateTime'][11:19]}"

        # f"{list_of_events[event]['result']['event']} ({list_of_events[event]['about']['ordinalNum']} P, {list_of_events[event]['about']['periodTimeRemaining']}): {list_of_events[event]['result']['description']}, @ {list_of_events[event]['about']['dateTime'][11:19]}")

        if ticks == 0:
            print(f"\nTick #{ticks + 1}: {latest_play}")
            recently_ticked_play.append(latest_play)
            ticks += 1

        elif ticks > 0 and latest_play not in recently_ticked_play:
            print(f"\nTick #{ticks + 1}: {latest_play}")
            recently_ticked_play.clear()
            recently_ticked_play.append(latest_play)
            ticks += 1

        # print(ticks)

        time.sleep(3)


def count_files_in_dir(my_dir):
    amount_of_files = 0
    for path in os.scandir(my_dir):
        if path.is_file():
            amount_of_files += 1

    return amount_of_files


if __name__ == '__main__':
    """
    Logic to process program based on command line arguments
    EX. If the user enters 'roster' followed by a team abbreviation, that team's roster will be obtained
    """
    if len(sys.argv) >= 3 and sys.argv[1] == 'roster':
        create_team_roster_json(sys.argv[2].upper())
    elif len(sys.argv) >= 2 and sys.argv[1] == 'id_lookup':
        team_id_lookup(sys.argv[2])
    elif len(sys.argv) >= 3 and sys.argv[1] == 'report':
        game_plays_report(sys.argv[2], sys.argv[3])
    elif len(sys.argv) >= 3 and sys.argv[1] == 'ticker':
        live_ticker(sys.argv[2])
    elif len(sys.argv) >= 3 and sys.argv[1] == 'ending_time':
        game_ending_time(sys.argv[2])
    else:
        globals()[sys.argv[1]]()
