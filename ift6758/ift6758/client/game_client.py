import pandas as pd
import numpy as np
import requests
import json
import logging
import math

logger = logging.getLogger(__name__)

#removed if not so that tracker won't accumulate after each run of app
with open('tracker.json', 'w') as outfile:
    data = {}
    json.dump(data, outfile)

class Game_Client:
    def __init__(self):
        logger.info(f"Initializing ClientGame; base URL: ")

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

    def tidy_one_game_data(self, game_info):
    # data_to_tidy = get_all_files_path_under(path)

        data_list = []

    # for j in tqdm(range(len(data_to_tidy))):
        
        data = game_info
     
        # with open(json_file) as json_file:
            # data = json.load(json_file)


        homeId =  data.get('homeTeam').get('id')
        awayId =  data.get('awayTeam').get('id')

        # plays = data.get("plays")

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
               
   
                    distance = self.get_distance(shooterTeamId,homeId,homeSide,x,y)
                    angle = self.get_angle(shooterTeamId,homeId,homeSide,x,y)
                    isGoal = 0
                    emptyNet = 0
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

                    new_row = {'gameId': ID, 'distance': distance, 'angle': angle, 'emptyNet': emptyNet, 'isGoal': isGoal, 'home_score': home_score,
                               'away_score': away_score}
                    data_list.append(new_row)
        df = pd.DataFrame(data_list)        
        # path =os.path.normpath(path) 
        # path.split('\\')[-2:]
        # csv_name = path.split('\\')[-2]+'_'+ path.split('\\')[-1]+'_clean'+'.csv'
        # folder = './ift6758/ift6758/data/data_tidy/'+csv_name

        # df.to_csv(folder, encoding='utf-8', index=False)

    def ping_game(self, game_id: str) -> pd.DataFrame:
        live = True
        
        game_info = self.get_game_data(self.compose_api_url(game_id))

        if game_info.get('gameState') == 'OFF':
            live = False
        
        # df = self.tidy_one_game_data(game_info)
        # home_score = df['home_score'].values[0]
        # away_score = df['away_score'].values[0]
        home_team = game_info['homeTeam']['name']['default']
        away_team = game_info['awayTeam']['name']['default']
        home_score = game_info['homeTeam']['score']
        away_score = game_info['awayTeam']['score']
        
        f = open('tracker.json')
        data = json.load(f)
        old_idx=0
        if game_id in data:
            old_idx=data[str(game_id)]['idx']
            data[str(game_id)]['idx'] = len(df)
        else:
            data[str(game_id)] = {}
            data[str(game_id)]['idx'] = len(df)
        with open('tracker.json', 'w') as outfile:
            json.dump(data, outfile) 
        df = df.reset_index().drop('index', axis=1)[old_idx:]        
        # df[df['team']==df['home']],df[df['team']==df['away']] 
        # return df, live, game_id, timeLeft, home_team, away_team, home_score, away_score
        return df, live, game_id, home_team, away_team, home_score, away_score