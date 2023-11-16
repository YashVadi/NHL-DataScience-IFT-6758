import pandas as pd
import os
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
            return 'shoot out'
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
        return 'shoot out'
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
        
def create_csv(folder_path):
    data_to_tidy = get_all_files_path_under(folder_path)
    #columns = ['gamePk','season','gameType','home','away',
    #'eventTypeId','shotType','shooter','goalie','eventPeriod','eventPeriodType','x','y']
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
                    

            new_row = {'gamePk':gamePk,'season':season,'gameType':gameType,'home':home,'away':away,
                        'eventTypeId':eventTypeId,'shotType':shotType,
                       'shooter':shooter,'shooterTeam':shooterTeam,'distance':distance ,'angle':angle,'goalie':goalie,
                       'eventPeriod':eventPeriod,
                       'eventPeriodType':eventPeriodType,'x':x,'y':y,'emptyNet':emptyNet,'isGoal':isGoal

                      }
            
            #df_to_concat = dd.from_pandas(pd.DataFrame(new_row,index=index)， npartitions=2)
            #df = dd.concat([df, df_to_concat])
            data_list.append(new_row)
    df = pd.DataFrame(data_list)        
    path =os.path.normpath(folder_path) 
    path.split('/')[-2:]
    csv_name = path.split('/')[-2]+'_'+ path.split('/')[-1]+'_clean'+'.csv'
    df.to_csv(csv_name, encoding='utf-8', index=False)
        
data_folder = 'data/'
folder_path_20162017P = data_folder + '2016-2017/P'
folder_path_20162017R = data_folder + '2016-2017/R'

folder_path_20172018P = data_folder + '2017-2018/P'
folder_path_20172018R = data_folder + '2017-2018/R'

folder_path_20182019P = data_folder  + '2018-2019/P'
folder_path_20182019R = data_folder  + '2018-2019/R'

folder_path_20192020P = data_folder  + '2019-2020/P'
folder_path_20192020R = data_folder  + '2019-2020/R'

folder_path_20202021P = data_folder  + '2020-2021/P'
folder_path_20202021R = data_folder  + '2020-2021/R'

create_csv(folder_path_20162017P)
create_csv(folder_path_20162017R)
create_csv(folder_path_20172018P)
create_csv(folder_path_20172018R)
create_csv(folder_path_20182019P)
create_csv(folder_path_20182019R)
create_csv(folder_path_20192020P)
create_csv(folder_path_20192020R)

df20162017R = pd.read_csv('2016-2017_R_clean.csv')
df20162017P = pd.read_csv('2016-2017_P_clean.csv')
df20162017 = pd.concat([df20162017R,df20162017P])
df20162017.to_csv('20162017_clean.csv', encoding='utf-8', index=False)

df20172018R = pd.read_csv('2017-2018_R_clean.csv')
df20172018P = pd.read_csv('2017-2018_P_clean.csv')
df20172018 = pd.concat([df20172018R,df20172018P])
df20172018.to_csv('20172018_clean.csv', encoding='utf-8', index=False)

df20182019R = pd.read_csv('2018-2019_R_clean.csv').sort_values(by='gamePk', ascending=True)
df20182019P = pd.read_csv('2018-2019_P_clean.csv').sort_values(by='gamePk', ascending=True)
df20182019 = pd.concat([df20182019R,df20182019P]).sort_values(by='gamePk', ascending=True)
df20182019.to_csv('20182019_clean.csv', encoding='utf-8', index=False)

df20192020R = pd.read_csv('2019-2020_R_clean.csv').sort_values(by='gamePk', ascending=True)
df20192020P = pd.read_csv('2019-2020_P_clean.csv').sort_values(by='gamePk', ascending=True)
df20192020 = pd.concat([df20192020R,df20192020P]).sort_values(by='gamePk', ascending=True)
df20192020.to_csv('20192020_clean.csv', encoding='utf-8', index=False)

df20162018 = pd.concat([df20162017 ,df20172018]).sort_values(by='gamePk', ascending=True)
df20162019 = pd.concat([df20162018 ,df20182019]).sort_values(by='gamePk', ascending=True)
df20162019 = pd.concat([df20162019 ,df20192020]).sort_values(by='gamePk', ascending=True)
df20162019.to_csv('20162019_clean.csv', encoding='utf-8', index=False)
