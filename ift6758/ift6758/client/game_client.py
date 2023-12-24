import pandas as pd
import numpy as np
import requests
import json
import logging
import math

logger = logging.getLogger(__name__)

#removed if not so that tracker won't accumulate after each run of app
with open('tracker.json', 'w') as outfile:
    history = {}
    json.dump(history, outfile)

class GameClient:
    def __init__(self):
        logger.info(f"Initializing ClientGame...")

    def compose_api_url (self, game_id):
        return "https://api-web.nhle.com/v1/gamecenter/" + game_id + "/play-by-play"

    def get_game_data (self, api_url):
        response = requests.get(api_url)
        return response.json()
    
    def get_distance(self, shooterTeamId, homeId, homeSide, x, y):
        if shooterTeamId == homeId:
            if homeSide == 'right':
                return  math.sqrt((x +100)**2 + (y)**2)
            if homeSide == 'left':
                return  math.sqrt((x -100)**2 + (y)**2)
        if shooterTeamId != homeId:
            if homeSide == 'right':
                return  math.sqrt((x - 100)**2 + (y)**2)
            if homeSide == 'left':
                return  math.sqrt((x + 100)**2 + (y)**2)
        
    def get_angle(self, shooterTeamId, homeId, homeSide, x, y):
        if shooterTeamId == homeId:
            if homeSide == 'right':
                a = abs(y)
                b = math.sqrt((x + 100)**2 + (y)**2)
                c = abs(x + 100)
                return math.degrees(math.acos((b**2 + c**2 - a**2)/(2*b*c)))
            if homeSide == 'left':
                a = abs(y)
                b = math.sqrt((x -100)**2 + (y)**2)
                c = abs(x - 100)
                return math.degrees(math.acos((b**2 + c**2 - a**2)/(2*b*c)))
        if shooterTeamId != homeId:
            if homeSide == 'right':
                a = abs(y)
                b = math.sqrt((x -100)**2 + (y)**2)
                c = abs(x - 100)
                return math.degrees(math.acos((b**2 + c**2 - a**2)/(2*b*c)))
            if homeSide == 'left':
                a = abs(y)
                b = math.sqrt((x + 100)**2 + (y)**2)
                c = abs(x + 100)
                return math.degrees(math.acos((b**2 + c**2 - a**2)/(2*b*c)))

    def tidy_one_game_data(self, json_file):
        data = json_file
    
        data_list = []
        homeId =  data.get('homeTeam').get('id')
        awayId =  data.get('awayTeam').get('id')

        plays = data.get("plays")

        ID = data.get('id')

        plays = data.get('plays')

        home_score = 0
        away_score = 0
        for i in range(len(plays)):

            if plays[i]['typeDescKey'] in ["missed-shot", "goal" ,'shot-on-goal']:
                details =  plays[i].get('details')
                if 'xCoord' in details.keys():
                    homeSide = plays[i]['homeTeamDefendingSide']
                    shooterTeamId = details['eventOwnerTeamId']
                    homeSide = plays[i]['homeTeamDefendingSide']

                    x = details['xCoord']
                    y = details['yCoord']
                    
                    timeRemaining = plays[i]['timeRemaining']
                    period = plays[i]['period']
                    
                    distance = self.get_distance(shooterTeamId,homeId,homeSide,x,y)
                    angle = self.get_angle(shooterTeamId,homeId,homeSide,x,y)
                    isGoal = 0
                    emptyNet = 0
                    if shooterTeamId == homeId:
                        home_or_away = 'home'
                    else:
                        home_or_away = 'away'
                    
                    if  plays[i]['typeDescKey'] ==  "goal":
                        isGoal = 1
                        if shooterTeamId == homeId:
                            home_score += 1
                            if int(plays[i].get('situationCode')[0]) == 0:
                                emptyNet= 1
                        if shooterTeamId == awayId:
                            away_score += 1
                            if int(plays[i].get('situationCode')[3]) == 0:
                                emptyNet = 1

                    new_row = {'gameId':ID, 'home_or_away': home_or_away, 'distance':distance, 'angle':angle, 'emptyNet':emptyNet,'isGoal':isGoal,' period': period, 'timeRemaining':timeRemaining, 'home_score':home_score, 'away_score':away_score}
                    data_list.append(new_row)
        df = pd.DataFrame(data_list)    
        return df       

    def ping_game(self, game_id: str) -> pd.DataFrame:
        live = True
        
        game_json_file = self.get_game_data(self.compose_api_url(game_id))

        if game_json_file.get('gameState') == 'OFF':
            live = False
        
        home_team = game_json_file['homeTeam']['name']['default']
        away_team = game_json_file['awayTeam']['name']['default']
        home_score = game_json_file['homeTeam']['score']
        away_score = game_json_file['awayTeam']['score']
        df = self.tidy_one_game_data(game_json_file)
        home_score = df['home_score'].values[-1]
        away_score = df['away_score'].values[-1]
        period = df[' period'].values[-1]
        timeRemaining = df['timeRemaining'].values[-1]
        
        ###############################################
        # The codes below are refered to github:
        # "https://github.com/haooyuee/nhl-shot-analysis/blob/main/milestone_3_nhl_app/ift6758/ift6758/client/game_client.py"
        ###############################################
        tracker = open('tracker.json')
        history = json.load(tracker)
        previous_idx = 0
        if game_id in history:
            previous_idx = history[str(game_id)]['idx']
            history[str(game_id)]['idx'] = len(df)
        else:
            history[str(game_id)] = {}
            history[str(game_id)]['idx'] = len(df)
        with open('tracker.json', 'w') as outfile:
            json.dump(history, outfile) 
        df = df.reset_index().drop('index', axis=1)[previous_idx:]   
        ###############################################
        ###############################################     

        return df, live, game_id, home_team, away_team, home_score, away_score, period, timeRemaining
    
if __name__ == "__main__":
    game_client = GameClient()
    df, live, game_id, home_team, away_team, home_score, away_score, period, timeRemaining = game_client.ping_game('2023020510')

    print(df)
    print("Game is live: " + str(live))
    print("Game ID is: " + str(game_id))
    print("Home team is: " + str(home_team))
    print("Away team is: " + str(away_team))
    print("Home score is: " + str(home_score))
    print("Away score is: " + str(away_score))
    print("period is: " + str(period))
    print("timeRemaining is: " + str(timeRemaining))