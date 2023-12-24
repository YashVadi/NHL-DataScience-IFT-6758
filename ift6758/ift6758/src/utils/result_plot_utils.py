import pandas as pd
import numpy as np
import os
from matplotlib import pyplot as plt
import seaborn as sns
from sklearn.metrics import roc_curve, auc
from sklearn.calibration import calibration_curve

import warnings
warnings.filterwarnings('ignore')


def plot_roc_multi(models, y_true):
    '''
    Plot ROC curves for multiple models in one figure.
    input: models - list of tuples (model_name, y_pred) for each model
           y_true - the true labels of validation data
    '''
    for model_name, y_pred in models:
        fpr, tpr, _ = roc_curve(y_true, y_pred)
        roc_auc = auc(fpr, tpr)
        plt.plot(fpr, tpr, label=f'{model_name} (AUC = {roc_auc:.2f})', linewidth=2.5)

    # Plot the random baseline
    plt.plot([0, 1], [0, 1], linestyle='--', color='black', label='Random Baseline')

    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic (ROC) Curve')
    plt.legend(loc='lower right')
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.show()

def plot_calibration_multi(models, y_true):
    '''
    Plot calibration curves for multiple models in one figure.
    input: models - list of tuples (model_name, y_pred) for each model
           y_true - the true labels of validation data
    '''
    for model_name, y_pred in models:
        prob_true, prob_pred = calibration_curve(y_true, y_pred, n_bins=10, strategy='uniform')
        plt.plot(prob_pred, prob_true, marker='o', label=f'{model_name}')

    # Plot the perfectly calibrated model
    plt.plot([0, 1], [0, 1], linestyle='--', color='black', label='Perfectly Calibrated')

    plt.xlabel('Mean Predicted Probability')
    plt.ylabel('Fraction of Positives')
    plt.title('Calibration Curve for Multiple Models')
    plt.legend(loc='upper left')
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.show()

def plot_goal_ratio_multi(models, y_true):
    '''
    Plot the cumulative proportion of goals for multiple models in one figure.
    input: models - list of tuples (model_name, y_pred) for each model
           y_true - the true labels of validation data
    '''
    bins = list(np.arange(0, 105, 5))
    bin_centers = list(np.arange(2.5, 100, 5.0))
    
    df_combined = pd.DataFrame()

    for model_name, y_pred in models:
        df_prob = pd.DataFrame({
            'goal_pred': y_pred,
            'goal': y_true,
            'model': model_name,
        })

        df_prob['shot'] = 1
        sum_goal = df_prob['goal'].sum()

        df_prob['percentile'] = df_prob['goal_pred'].rank(pct=True) * 100
        df_prob['goal_perc_bins'] = pd.cut(df_prob['percentile'], bins, labels=bin_centers)

        df_prob_binned = df_prob[['goal_perc_bins', 'shot', 'goal', 'model']].groupby(['goal_perc_bins', 'model'], observed=False).sum().reset_index()

        df_prob_binned['goal_rate'] = (df_prob_binned['goal'] / df_prob_binned['shot'])
        df_prob_binned['goal_cum'] = (df_prob_binned['goal'] / sum_goal)
        df_prob_binned['goal_cumsum'] = 1 - df_prob_binned['goal_cum'].cumsum()
        
        df_combined = pd.concat([df_combined, df_prob_binned], ignore_index=True)

    fig, ax = plt.subplots()
    plt.title('Goal rate')
    sns.lineplot(x='goal_perc_bins', y='goal_rate', hue='model', data=df_combined, linewidth=2.5, marker='o')
    plt.xlabel('Shot Probability Model Percentile')
    plt.ylabel('Goals / (Shots + Goals)')
    ax.set_xlim(left=100, right=0)
    ax.set_ylim(bottom=0, top=1)
    plt.xticks(np.arange(0, 120, 20))
    plt.legend(loc='upper right')
    
    plt.grid()
    plt.show()

def plot_cumu_goal_multi(models, y_true):
    '''
    Plot the cumulative proportion of goals for multiple models in one figure.
    input: models - list of tuples (model_name, y_pred) for each model
           y_true - the true labels of validation data
    '''
    bins = list(np.arange(0, 105, 5))
    bin_centers = list(np.arange(2.5, 100, 5.0))
    
    df_combined = pd.DataFrame()

    for model_name, y_pred in models:
        df_prob = pd.DataFrame({
            'goal_pred': y_pred,
            'goal': y_true,
        })

        df_prob['shot'] = 1
        sum_goal = df_prob['goal'].sum()

        df_prob['percentile'] = df_prob['goal_pred'].rank(pct=True) * 100
        df_prob['goal_perc_bins'] = pd.cut(df_prob['percentile'], bins, labels=bin_centers)

        df_prob_binned = df_prob[['goal_perc_bins', 'shot', 'goal']].groupby(['goal_perc_bins'], observed=False).sum().reset_index()

        df_prob_binned['goal_rate'] = (df_prob_binned['goal'] / df_prob_binned['shot'])
        df_prob_binned['goal_cum'] = (df_prob_binned['goal'] / sum_goal)
        df_prob_binned['goal_cumsum'] =( 1 - df_prob_binned['goal_cum'].cumsum())*100
        
        df_prob_binned['model'] = model_name
        df_combined = pd.concat([df_combined, df_prob_binned], ignore_index=True)

    fig, ax = plt.subplots()
    plt.title('Cumulative Proportion of Goals for Multiple Models')
    sns.lineplot(x='goal_perc_bins', y='goal_cumsum', hue='model', data=df_combined, linewidth=2.5, marker='o')
    plt.xlabel('Shot Probability Model Percentile')
    plt.ylabel('Cumulative Proportion of Goals')
    ax.set_xlim(left=100, right=0)
    ax.set_ylim(bottom=0, top=100)
    plt.xticks(np.arange(0, 120, 20))
    plt.legend(loc='upper left')
    plt.show()

