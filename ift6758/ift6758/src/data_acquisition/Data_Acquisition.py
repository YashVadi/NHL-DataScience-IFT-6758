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
    return "https://api-web.nhle.com/v1/gamecenter/" + game_id + "/play-by-play"

def get_game_data (api_url):
    response = requests.get(api_url)
    return response.json()

def create_json_file (year, type, round, matchup, game):
    game_id = None
    if type == "R":
        game_id = compose_regSeason_game_id(year, game)
    else:
        game_id = compose_playoff_game_id(year, round, matchup, game)

    file_path = "./ift6758/ift6758/data/data_json/" + str(year) + "-" + str(year+1) + "/" + str(type) + "/" + game_id + ".json" 
    if not Path(file_path).exists():
        try:
            json_data = get_game_data(compose_api_url(game_id))

            if json_data.get("gameState") == "OFF":
                with open(file_path, "w") as outfile:    
                    json.dump(json_data, outfile)
        except:
            print("No game data for " + game_id)

def __main__ ():
    for year in range(2019, 2023):
        print(year)
        # type 02 is regular season, type 03 is playoff
        for type in ["R", "P"]:
            print(type)
            if type == "R":
                if year == 2019:
                    Path("./ift6758/ift6758/data/data_json/" + str(year) + "-" + str(year+1) + "/R").mkdir(parents=True, exist_ok=True)     
                    for game in range(1, 1083):
                        create_json_file(year, type, None, None, game)
                elif year == 2020: 
                    Path("./ift6758/ift6758/data/data_json/" + str(year) + "-" + str(year+1) + "/R").mkdir(parents=True, exist_ok=True)    
                    for game in range(1, 869):
                        create_json_file(year, type, None, None, game)
                elif 2021 == year or year == 2022:
                    Path("./ift6758/ift6758/data/data_json/" + str(year) + "-" + str(year+1) + "/R").mkdir(parents=True, exist_ok=True)    
                    for game in range(1, 1313):
                        create_json_file(year, type, None, None, game)
                                        
            else: 
                Path("./ift6758/ift6758/data/data_json/" + str(year) + "-" + str(year+1) + "/P").mkdir(parents=True, exist_ok=True)
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


# def get_one_game_json(game_id):
#     api_url = "https://api-web.nhle.com/v1/gamecenter/" + game_id + "/play-by-play"
#     response = requests.get(api_url)
#     json_data = response.json()
#     return json_data