import requests   
from pathlib import Path     
import json       

def compose_4digit_game_id (game):
    if game < 10:
        game = "000" + str(game)
    elif game < 100:
        game = "00" + str(game)
    elif game < 1000:
        game = "0" + str(game)
    else:
        game = str(game)
    return game

def compose_regSeason_game_id (year, game):
    return str(year) + "02" + str(compose_4digit_game_id(game))

def compose_playoff_game_id (year, round, matchup, game):
    return str(year) + "030" + str(round) + str(matchup) + str(game)

def compose_api_url (game_id):
    return "https://statsapi.web.nhl.com/api/v1/game/" + game_id + "/feed/live/"

def get_game_data (api_url):
    response = requests.get(api_url)
    return response.json()

def create_json_file (year, type, round, matchup, game):
    game_id = None
    if type == "R":
        game_id = compose_regSeason_game_id(year, game)
    else:
        game_id = compose_playoff_game_id(year, round, matchup, game)

    file_path = "./" + str(year) + "-" + str(year+1) + "/" + str(type) + "/" + game_id + ".json" 
    if not Path(file_path).exists():
        json_data = get_game_data(compose_api_url(game_id))
        try:
            if json_data.get("gameData").get("status").get("abstractGameState") == "Final":
                with open(file_path, "w") as outfile:    
                    json.dump(json_data, outfile)
        except:
            print("No game data for " + game_id)

def __main__ ():
    for year in range(2016, 2021):
        print(year)
        # type 02 is regular season, type 03 is playoff
        for type in ["R", "P"]:
            print(type)
            if type == "R":
                if year == 2016:
                    Path("./2016-2017/R").mkdir(parents=True, exist_ok=True)
                    for game in range(1, 1231):
                        create_json_file(year, type, None, None, game)
                elif 2017 <= year <= 2019:
                    Path("./" + str(year) + "-" + str(year+1) + "/R").mkdir(parents=True, exist_ok=True)    
                    for game in range(1, 1272):
                        create_json_file(year, type, None, None, game)
                else: 
                    Path("./" + str(year) + "-" + str(year+1) + "/R").mkdir(parents=True, exist_ok=True)    
                    for game in range(1, 868):
                        create_json_file(year, type, None, None, game)
                                        
            else: 
                Path("./" + str(year) + "-" + str(year+1) + "/P").mkdir(parents=True, exist_ok=True)
                for round in range(1, 5):
                    if round == 1:
                        for matchup in range(1,9):
                            for game in range(1,8):
                                create_json_file(year, type, round, matchup, game)
                    elif round == 2:
                        for matchup in range(1,5):
                            for game in range(1,8):
                                create_json_file(year, type, round, matchup, game)
                    elif round == 3:
                        for matchup in range(1,3):
                            for game in range(1,8):
                                create_json_file(year, type, round, matchup, game)
                    else:
                        for game in range(1,8):
                            create_json_file(year, type, round,1, game)
                        
if __name__ == "__main__":
    __main__()
