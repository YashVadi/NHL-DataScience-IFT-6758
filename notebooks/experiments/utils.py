import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import numpy as np

def pre_processing(df,fill_nan_mod = False,drop_nan = False,oneHot = False):
    
    df_val = df[(df['eventType'] == 'Shot') | (df['eventType'] == 'Goal')]
    X = df_val[ ['shotType', 'distance' ,'angle','isGoal','emptyNet','eventPeriod','x','y','game_time',\
         'timeFromLastEvent','prevEventType', 'distFromPrev','prevEventX','prevEventY', \
         'isRebound','changeInAngle', 'speed']  ]
    X = X.dropna(subset=['shotType']).reset_index(drop=True)

    if drop_nan == True:
        X = X.dropna()
        X = X.reset_index(drop = True)

    if fill_nan_mod == True:
        
        for column in X.columns:
            
            mode_value = X[column].mode()[0]
            
            X[column] = X[column].fillna(mode_value)


    if oneHot == True:
        ohe = OneHotEncoder()
        
        # Assuming X is your input DataFrame and 'shotType' and 'prevEventType' are the columns to be encoded.
        encoded_values = ohe.fit_transform(X[['shotType', 'prevEventType']])
        
        # Convert the sparse matrix to a dense array
        encoded_values_dense = encoded_values.toarray()
        
        # Now, create the DataFrame with the correct number of column names
        df_encoded = pd.DataFrame(encoded_values_dense, columns=ohe.get_feature_names_out(['shotType', 'prevEventType']))
        X = pd.concat([X.drop(['shotType', 'prevEventType'], axis=1), df_encoded], axis=1)

    return X

def combine_df(path_train_list,oneHot = False):
    if oneHot == True:
        df = pd.read_csv(path_train_list[0])
        df = pre_processing(df,oneHot = True)
        for i in range(1,len(path_train_list)):
            df_temp = pd.read_csv(path_train_list[i])
            df_temp = pre_processing(df_temp,oneHot = True)
            df = pd.concat([df,df_temp])
        df = df.reset_index(drop = True)
    if oneHot == False:
        df = pd.read_csv(path_train_list[0])
        df = pre_processing(df)
        for i in range(1,len(path_train_list)):
            df_temp = pd.read_csv(path_train_list[i])
            df_temp = pre_processing(df_temp)
            df = pd.concat([df,df_temp])
        df = df.reset_index(drop = True)
    return df

def get_X_y(data):
    y = data['isGoal']
    X = data.drop('isGoal',axis = 1)
    return X,y

def fill_nan_with_mode(df): 
    for column in df.columns:
        mode = df[column].mode()[0]
        df[column].fillna(mode, inplace=True)
        
def replace_inf(df):
    max = np.sort(df['speed'].unique())[-3]
    return df['speed'].replace(np.inf,max)

def get_95_PCA(X_train):
    fill_nan_with_mode(X_train)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)

    pca = PCA(n_components=0.95)
    pca.fit(X_train_scaled)
    return pca