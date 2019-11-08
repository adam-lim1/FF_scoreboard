from flask import Flask, render_template, redirect
import datetime
import requests
import configparser
import sys,os,os.path
import pickle
import pandas as pd
import numpy as np
import random

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import helpers as helpers

app = Flask(__name__)

################################################################################
##  ******************* GET CONFIG INFO *******************
################################################################################
config = configparser.RawConfigParser()
config.read('config.txt')

# Google Sheets Parameters
SAMPLE_SPREADSHEET_ID = config.get('Sheets Parameters', 'SAMPLE_SPREADSHEET_ID')
SAMPLE_RANGE_NAME = config.get('Sheets Parameters', 'SAMPLE_RANGE_NAME')

# League Parameters
multiplierList = [float(x) for x in config.get('League Parameters', 'multiplierList').split(', ')]

# ESPN Parameters
leagueID = config.get('ESPN Parameters', 'leagueID')
year = config.get('ESPN Parameters', 'year')
swid_cookie = config.get('ESPN Parameters', 'swid_cookie')
s2_cookie = config.get('ESPN Parameters', 's2_cookie')

################################################################################
##  ******************* GET DATA FROM GOOGLE/ESPN *******************
################################################################################

initialTime=datetime.datetime.now()

##  ******************* PROCESS INPUT FROM GOOGLE SHEETS *******************
# Get data from sheets
sheetsDF = helpers.getSheetsData(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME)

# Randomly select multipliers
multiplierPivot, unstacked_multiplierDF = helpers.getMultipliers(sheetsDF, multiplierList)
multiplierDF = sheetsDF.merge(unstacked_multiplierDF, left_on=['Team', 'Week'], right_on=['Team', 'Week'], how='left')

##  ******************* PULL MATCHUPS AND SCORING FROM ESPN *******************
# Team names and ID
teamsDF = helpers.getTeamsKey(leagueID, year, swid_cookie, s2_cookie)


################################################################################
##  ******************* RENDER PAGES WITH FLASK *******************
################################################################################

@app.route('/scoreboard')
def scoreboard_page():
    ## Find current week and redirect to there
    currentWeek = helpers.getCurrentWeek(leagueID, year, swid_cookie, s2_cookie)
    currentWeek = str(currentWeek)

    return redirect('/scoreboard/week{}'.format(currentWeek))

### Generic routing function to cover each week
@app.route('/scoreboard/week<viewWeek>')
def weekGeneric_page(viewWeek):

    viewWeek = int(viewWeek)

    # GET SHEETS INPUT
    sheetsDF = helpers.getSheetsData(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME)
    multiplierPivot, unstacked_multiplierDF = helpers.getMultipliers(sheetsDF, multiplierList)
    multiplierDF = sheetsDF.merge(unstacked_multiplierDF, left_on=['Team', 'Week'], right_on=['Team', 'Week'], how='left')

    # GET TEAM SCORES FOR WEEK
    scoreboardDF = helpers.getWeekScoreboard(leagueID, year, swid_cookie, s2_cookie, viewWeek)
    scoreboardDF = scoreboardDF.merge(teamsDF, left_on='teamID', right_index=True, how='left')
    scoreboardDF = scoreboardDF.rename(columns={'FullTeamName':'Team'})

    # GET PLAYER SCORES FOR WEEK
    playerScoresDF = helpers.getWeekPlayerScores(leagueID, year, swid_cookie, s2_cookie, viewWeek)

    # JOIN
    adjustedScores = helpers.mergeScores(teamsDF, scoreboardDF, multiplierDF, playerScoresDF)
    scoreboardDict = helpers.scoresToDict(adjustedScores, int(teamsDF.shape[0]/2))

    return render_template('scoreboard.html',
                            input1='Week {}'.format(viewWeek),
                            scoreboardDict=scoreboardDict,
                            time=datetime.datetime.now())

@app.route('/MultiplierResults')
def multiplier_page():

    # ToDo - Treatment to not reval multiplier if gametime has not yet passed

    # Get data from sheets
    sheetsDF = helpers.getSheetsData(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME)

    # Randomly select multipliers
    multiplierPivot, unstacked_multiplierDF = helpers.getMultipliers(sheetsDF, multiplierList)


    ################ TO DO #####################
    # REPLACE THIS WITH GOOGLE SHEETS MUTIPLIER WRITE
    ################ TO DO #####################
    multiplierPivot = multiplierPivot.reset_index().rename(columns={'index':'Team'})

    currentWeek = helpers.getCurrentWeek(leagueID, year, swid_cookie, s2_cookie)
    multiplierPivot[currentWeek] = ' '

    ###### WRITE TO GOOGLE SHEETS INFO - ABSTRACT THIS ####
    range_name = 'Multipliers!A:L'
    value_input_option = 'RAW'

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()

    values = [
    [str(x) for x in list(multiplierPivot.columns)],
    [float(x) if type(x) != str else x for x in list(multiplierPivot.iloc[0])],
    [float(x) if type(x) != str else x for x in list(multiplierPivot.iloc[1])],
    [float(x) if type(x) != str else x for x in list(multiplierPivot.iloc[2])],
    [float(x) if type(x) != str else x for x in list(multiplierPivot.iloc[3])],
    [float(x) if type(x) != str else x for x in list(multiplierPivot.iloc[4])],
    [float(x) if type(x) != str else x for x in list(multiplierPivot.iloc[5])],
    [float(x) if type(x) != str else x for x in list(multiplierPivot.iloc[6])],
    [float(x) if type(x) != str else x for x in list(multiplierPivot.iloc[7])],
    [float(x) if type(x) != str else x for x in list(multiplierPivot.iloc[8])],
    [float(x) if type(x) != str else x for x in list(multiplierPivot.iloc[9])],
    [float(x) if type(x) != str else x for x in list(multiplierPivot.iloc[10])],
    [float(x) if type(x) != str else x for x in list(multiplierPivot.iloc[11])]
    ]
    body = {
        'values': values
    }

    service.spreadsheets().values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                       range=range_name,
                                       valueInputOption=value_input_option,
                                       body=body).execute()


    ##########################

    # for i in range(1,17+1): # Hardcoded number of matchup weeks
    #     try:
    #         multiplierPivot[str(i)] = multiplierPivot[str(i)].apply(lambda x: str(x))
    #     except:
    #         multiplierPivot[str(i)] = ''
    #
    # multiplierDict = multiplierPivot.reset_index().rename(columns={'index':'Team'}).to_dict(orient='index')

    return render_template('multipliers_GS.html',
                            time=datetime.datetime.now())
