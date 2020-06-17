import datetime
import requests
import configparser
import sys,os,os.path
import pickle
import pandas as pd
import numpy as np
import random

def updateMultiplier(currentWeek, teamID, multiplier_db_table):
    now = datetime.datetime.now()
    seed = hash((teamID, now))
    random.seed(seed)

    if currentWeek > 1: # Week 2+
        # Get multiplier info from previous week
        response = multiplier_db_table.get_item(Key={'week':str(currentWeek-1), 'teamID':teamID})
        last_multiplier = float(response['Item']['Multiplier'])
        last_available = eval(response['Item']['Available Multipliers'])
        availible_multipliers = [x for x in last_available if x != last_multiplier]

    else: # Week 1
        response = multiplier_db_table.get_item(Key={'week':str(currentWeek), 'teamID':teamID})
        availible_multipliers = eval(response['Item']['Available Multipliers'])

    selected_multiplier = random.choice(availible_multipliers)
    update_response = multiplier_db_table.put_item(Item={'week':str(currentWeek),
                                'teamID': teamID,
                                'Multiplier': str(selected_multiplier),
                                'Available Multipliers': str(availible_multipliers),
                                'Hash': seed})
    return update_response


def mergeScores(teamsDF, scoreboardDF, playerScoresDF):
    '''
    [TO BE COMPLETED]
    :param teamsDF (DataFrame):  Nbr Rows = {n Teams}. Cols = [FullTeamName]
    :param scoreboardDF (DataFrame): Nbr Rows = {n Teams}. Cols = [Week, matchupID, teamID, Points, home_away]
    :param playerScoresDF (DataFrame): Nbr Rows = {n Teams * nbr Players / Team}. Cols = [Week, Team ID, Player, Slot, Pos, Status, Proj, Actual]
    :return (DataFrame): Nbr Rows = {n Teams}. Cols = [TO BE COMPLETED]
    '''

    df = scoreboardDF.merge(teamsDF, left_on='teamID', right_index=True, how='left')
    #df = df.merge(multiplierDF, left_on=['Week', 'FullTeamName'], right_on=['Week', 'Team'], how='left')
    df = df.merge(playerScoresDF, left_on=['Week', 'teamID', 'Multiplayer'], right_on=["Week", 'Team ID', 'Player'], how='left')
    df = df[['Week', 'matchupID','home_away', 'Points', 'FullTeamName', 'Multiplayer', 'Multiplier', 'Actual']] # 'Timestamp',

    df['Multiplier'] = np.where(df['Actual'].isnull()==True, None, df['Multiplier']) # Adjust non-locked multipliers here
    df['Adjustment'] = -1*(1-df['Multiplier'])*df['Actual']
    df['AdjustedScore'] = df['Adjustment'] + df['Points']
    df['AdjustedScore'] = np.where(df['AdjustedScore'].isnull()==True, df['Points'], df['AdjustedScore'])

    return df

def scoresToDict(scoreboardDF, nbrGames):
    '''
    Convert Pandas DataFrame of scores to dictionary datatype so it can be passed as param to Flask page
    :param scoreboardDF (DataFrame): Nbr Rows = {n Teams}. Cols = [Week, matchupID, teamID, Points, home_away]
    :param nbrGames (int): Number of fantasy matchups per week (i.e. # Teams / 2)
    :return (dict): [KEY:VALUES PAIRS TO BE COMPLETED]
    '''
    scoreboardDict = {}
    for game in range(1, nbrGames + 1):
        matchupDict = {}
        for home_away in ["Home", "Away"]:
            teamDict = {
                'Team': scoreboardDF.query('matchupID == {}'.format(game)).query('home_away=="{}"'.format(home_away))['FullTeamName'].values[0],
                'Multiplayer': scoreboardDF.query('matchupID == {}'.format(game)).query('home_away=="{}"'.format(home_away))['Multiplayer'].values[0],
                'Multiplier': scoreboardDF.query('matchupID == {}'.format(game)).query('home_away=="{}"'.format(home_away))['Multiplier'].values[0],
                'Score Adjustment': scoreboardDF.query('matchupID == {}'.format(game)).query('home_away=="{}"'.format(home_away))['Adjustment'].values[0],
                'Adjusted Score': scoreboardDF.query('matchupID == {}'.format(game)).query('home_away=="{}"'.format(home_away))['AdjustedScore'].values[0],
            }
            matchupDict[home_away] = teamDict
        scoreboardDict[game] = matchupDict

    return scoreboardDict
