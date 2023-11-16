import pandas as pd
import os
import numpy as np
import json
from datetime import datetime
from tqdm import tqdm
import math
from dateutil import parser


def get_all_files_path_under(folder_path):

    all_jsons = []

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            all_jsons.append( os.path.normpath (file_path) )
    return all_jsons

def time_difference(datetime_str1,datetime_str2):
    # Define your two datetime strings
    datetime_str1 = '2017-04-12T23:00:00Z'
    datetime_str2 = '2017-04-13T01:41:46Z'

    # Parse the datetime strings into datetime objects
    datetime_obj1 = parser.parse(datetime_str1)
    datetime_obj2 = parser.parse(datetime_str2)

    # Calculate the time difference
    time_difference = datetime_obj2 - datetime_obj1

    # Extract hours and minutes from the time difference
    hours, remainder = divmod(time_difference.total_seconds(), 3600)
    minutes = remainder / 60

    # Print the result
    return f"{int(hours)} hours and {int(minutes)} minutes"

def get_periodes(data):
    periods = data.get('liveData').get('linescore').get('periods')
    my_dict = {i: None for i in range(1,len(periods)+1)}
    for i in range(len(periods)):
        my_dict[i+1] = {'home': periods[i].get('home').get('rinkSide'), 'away':periods[i].get('away').get('rinkSide') }
    return my_dict

def home_or_away(shooterTeam,home,away):
    if shooterTeam == home:
        return str('home')
    if shooterTeam == away:
        return str('away')
    
def get_distance(eventPeriod,home_away,x,y,rink_info):
        if eventPeriod == 5:
            return None
        if home_away == 'home':
            rinkSide = rink_info[eventPeriod]['home']
            if rinkSide == 'right':
                return  math.sqrt((x +100)**2 + (y)**2)
            if rinkSide == 'left':
                return  math.sqrt((x -100)**2 + (y)**2)
        if home_away == 'away':
            rinkSide = rink_info[eventPeriod]['away']
            if rinkSide == 'right':
                return  math.sqrt((x +100)**2 + (y)**2)
            if rinkSide == 'left':
                return  math.sqrt((x -100)**2 + (y)**2)
            
def get_angle(eventPeriod,home_away,x,y,rink_info):
    if eventPeriod == 5:
        return None
    if home_away == 'home':
        rinkSide = rink_info[eventPeriod]['home']
        if rinkSide == 'right':
            a = abs(y)
            b = math.sqrt((x + 100)**2 + (y)**2)
            c = abs(x + 100)
            return math.degrees(math.acos((b**2 + c**2 - a**2)/(2*b*c)))
        if rinkSide == 'left':
            a = abs(y)
            b = math.sqrt((x -100)**2 + (y)**2)
            c = abs(x - 100)
            return math.degrees(math.acos((b**2 + c**2 - a**2)/(2*b*c)))
    if home_away == 'away':
        rinkSide = rink_info[eventPeriod]['away']
        if rinkSide == 'right':
            a = abs(y)
            b = math.sqrt((x + 100)**2 + (y)**2)
            c = abs(x + 100)
            return math.degrees(math.acos((b**2 + c**2 - a**2)/(2*b*c)))
        if rinkSide == 'left':
            a = abs(y)
            b = math.sqrt((x -100)**2 + (y)**2)
            c = abs(x - 100)
            return math.degrees(math.acos((b**2 + c**2 - a**2)/(2*b*c)))
        
def calculate_change_in_angle(df):
    df = df.copy()

    df['changeInAngle'] = 0
    rebound_shot_mask = df['isRebound']
    df.loc[rebound_shot_mask, 'changeInAngle'] = np.abs(df['angle'] - df['angle'].shift(1))
    return df

def calculate_speed_from_prev(df):
    df = df.copy()
    df['speed'] = df['distFromPrev']/df['timeFromLastEvent']
    return df

def create_csv(folder_path, save_dir):
    data_to_tidy = get_all_files_path_under(folder_path)
    #columns = ['gamePk','season','gameType','home','away',
 #'eventTypeId','shotType','shooter','goalie','eventPeriod','eventPeriodType','x','y'

#]
    #df = dd.from_pandas(pd.DataFrame(columns = columns), npartitions=1)
    data_list = []
    for j in tqdm(range(len(data_to_tidy))):
        json_file = data_to_tidy[j]

        with open(json_file) as json_file:
            data = json.load(json_file)

        gamePk = data.get('gamePk')

        gameData = data.get('gameData')
        game = gameData.get('game')
        season = game.get('season')
        gameType = game.get('type')

        teams = gameData.get('teams')
        home =  teams.get('home').get('name')
        away =  teams.get('away').get('name')

        rink_info = get_periodes(data)
        plays = data.get('liveData').get('plays').get('allPlays')

        for i in range(len(plays)):

            play = plays[i]
            about= play.get('about')
            res = play.get('result')
            eventTypeId = res.get('eventTypeId')
            eventType = res.get('event')

            eventPeriod = about.get('period')
            eventPeriodType = about.get('periodType')


            shotType = shooter = goalie =shooterTeam = shotResult= distance = angle = None
            isGoal = 0
            emptyNet = 0
            players = play.get('players')

            players = play.get('players')
            if eventTypeId == 'SHOT':
                shotType =  res.get('secondaryType')
                shooterTeam = play.get('team').get('name')
                for player in players:
                    if player.get('playerType') == "Shooter":
                        shooter = player.get('player').get('fullName')
                    if  player.get('playerType') == "Goalie":
                        goalie = player.get('player').get('fullName')

            if eventTypeId == 'GOAL':
                shotType =  res.get('secondaryType')
                shooterTeam = play.get('team').get('name')
                isGoal = 1
                if res.get('emptyNet') == True:
                    emptyNet = 1
                for player in players:
                    if player.get('playerType') == 'Scorer':
                        shooter = player.get('player').get('fullName')
                    if  player.get('playerType') == "Goalie":
                        goalie = player.get('player').get('fullName') +'(failed)'

            if play.get('coordinates') == {}:
                x = None
                y = None
            else:
                for coord in play.get('coordinates'):
                    if coord == 'x':
                        x = play.get('coordinates')['x']
                    if coord == 'y':
                        y = play.get('coordinates')['y']
            if shooterTeam is not None:
                if play.get('coordinates') != {}:
                    home_away = home_or_away(shooterTeam,home,away)
                    distance =  get_distance(eventPeriod,home_away,x,y,rink_info)
                    angle = get_angle(eventPeriod,home_away,x,y,rink_info)

            ###### Feature engineering-2 ######

            period = play['about']['period']
            period_time = play['about']['periodTime']
            # assuming each play is of 20 mins
            game_time = (int(period) - 1) * 20 * 60 + int(period_time.split(':')[0]) * 60 + int(period_time.split(':')[1])
            eventID = play['about']['eventId']

            prev_event = plays[i-1]
            prev_eventID = prev_event['about']['eventId']
            prev_event_type = prev_event['result']['eventTypeId']
            prev_event_x = prev_event['coordinates']['x'] if 'x' in prev_event['coordinates'] else None
            prev_event_y = prev_event['coordinates']['y'] if 'y' in prev_event['coordinates'] else None

            try:
                dist_from_prev = np.linalg.norm(np.array([x,y]) - np.array([prev_event_x, prev_event_y]))
            except:
                dist_from_prev = None

            prev_event_period = int(prev_event['about']['period'])
            prev_event_period_time = prev_event['about']['periodTime']
            game_time_prev_event = (prev_event_period - 1) * 20 * 60 + int(prev_event_period_time.split(':')[0]) * 60 + \
                                int(prev_event_period_time.split(':')[1])

            time_from_last_event = game_time - game_time_prev_event

            is_rebound = True if prev_event_type == 'SHOT' and prev_event['team']['name'] == shooterTeam else False
            ##############################

            new_row = {
                'gamePk':gamePk,
                'season':season,
                'gameType':gameType,
                'home':home,
                'away':away,
                'eventTypeId':eventTypeId,
                'eventType': eventType,
                'shotType':shotType,
                'shooter':shooter,
                'shooterTeam':shooterTeam,
                'distance':distance ,
                'angle':angle,
                'goalie':goalie,
                'eventPeriod':eventPeriod,
                'eventPeriodType':eventPeriodType,
                'x':x,
                'y':y,
                'emptyNet':emptyNet,
                'isGoal':isGoal,

                ###### FE-2 ######
                'game_time':game_time,
                'eventID':eventID,
                'prevEventID':prev_eventID,
                'timeFromLastEvent':time_from_last_event,
                'prevEventX' : prev_event_x,
                'prevEventY' : prev_event_y,
                'prevEventType' :prev_event_type,
                'distFromPrev' :dist_from_prev,
                'isRebound' :is_rebound
                }

            #df_to_concat = dd.from_pandas(pd.DataFrame(new_row,index=index)， npartitions=2)
            #df = dd.concat([df, df_to_concat])
            data_list.append(new_row)

    df = pd.DataFrame(data_list)
    df = calculate_change_in_angle(df)
    df = calculate_speed_from_prev(df)
    path =os.path.normpath(folder_path)
    path.split('/')[-2:]
    csv_name = path.split('/')[-2]+'_'+ path.split('/')[-1]+'_clean'+'.csv'
    df.to_csv(os.path.join(save_dir, csv_name), encoding='utf-8', index=False)


def main():
    data_folder = "data/raw/"
    save_dir = 'data/FE2/'

    folder_path_20162017P = data_folder + '2016-2017/P'
    folder_path_20162017R = data_folder + '2016-2017/R'
    create_csv(folder_path_20162017R, save_dir)
    create_csv(folder_path_20162017P, save_dir)
    df20162017R = pd.read_csv(save_dir+'2016-2017_R_clean.csv')
    df20162017P = pd.read_csv(save_dir+'2016-2017_P_clean.csv')
    df20162017 = pd.concat([df20162017R,df20162017P])
    df20162017.to_csv(save_dir+'20162017_clean.csv', encoding='utf-8', index=False)

    folder_path_20172018P = data_folder + '2017-2018/P'
    folder_path_20172018R = data_folder + '2017-2018/R'
    create_csv(folder_path_20172018R, save_dir)
    create_csv(folder_path_20172018P, save_dir)
    df20172018R = pd.read_csv(save_dir+'2017-2018_R_clean.csv')
    df20172018P = pd.read_csv(save_dir+'2017-2018_P_clean.csv')
    df20172018 = pd.concat([df20172018R,df20172018P])
    df20172018.to_csv(save_dir+'20172018_clean.csv', encoding='utf-8', index=False)

    folder_path_20182019P = data_folder + '2018-2019/P'
    folder_path_20182019R = data_folder + '2018-2019/R'
    create_csv(folder_path_20182019R, save_dir)
    create_csv(folder_path_20182019P, save_dir)
    df20182019R = pd.read_csv(save_dir+'2018-2019_R_clean.csv')
    df20182019P = pd.read_csv(save_dir+'2018-2019_P_clean.csv')
    df20182019 = pd.concat([df20182019R,df20182019P])
    df20182019.to_csv(save_dir+'20182019_clean.csv', encoding='utf-8', index=False)

    folder_path_20192020R = os.path.join(data_folder, '2019-2020/R')
    folder_path_20192020P = os.path.join(data_folder, '2019-2020/P')
    create_csv(folder_path_20192020R, save_dir)
    create_csv(folder_path_20192020P, save_dir)
    df20192020R = pd.read_csv(save_dir+'2019-2020_R_clean.csv')
    df20192020P = pd.read_csv(save_dir+'2019-2020_P_clean.csv')
    df20192020 = pd.concat([df20192020R, df20192020P])
    df20192020.to_csv(save_dir+'20192020_clean.csv', encoding='utf-8', index=False)

    folder_path_20202021R = os.path.join(data_folder, '2020-2021/R')
    folder_path_20202021P = os.path.join(data_folder, '2020-2021/P')
    create_csv(folder_path_20202021R, save_dir)
    create_csv(folder_path_20202021P, save_dir)
    df20202021R = pd.read_csv(save_dir+'2020-2021_R_clean.csv')
    df20202021P = pd.read_csv(save_dir+'2020-2021_P_clean.csv')
    df20202021 = pd.concat([df20202021R, df20202021P])
    df20202021.to_csv(save_dir+'20202021_clean.csv', encoding='utf-8', index=False)
    
    df20162018 = pd.concat([df20162017 ,df20172018]).sort_values(by='gamePk', ascending=True)
    df20162019 = pd.concat([df20162018 ,df20182019]).sort_values(by='gamePk', ascending=True)
    df20162019 = pd.concat([df20162019 ,df20192020]).sort_values(by='gamePk', ascending=True)
    df20162019.to_csv(save_dir+'20162019_clean.csv', encoding='utf-8', index=False)



if __name__ == '__main__':
    main()