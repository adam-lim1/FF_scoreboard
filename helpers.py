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

def getSheetsData(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME, fillNullValue=np.nan):
    # ToDo: Complete function docstring

    #### CALL SHEET API
    if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME).execute()

    ## CONVERT TO PANDAS DF
    header = result.get('values', [])[0]
    values = result.get('values', [])[1:]

    outputLists = []
    for i in values:
        defaultRow = [fillNullValue]*len(header)
        defaultRow[:len(i)] = i
        defaultRow = [fillNullValue if x  == '' else x for x in defaultRow]
        outputLists.append(defaultRow)
    df = pd.DataFrame(outputLists, columns=header)
    df = df.rename(columns={"Select Team": "Team",
                            "Enter Multi-Player": "Multiplayer",
                            "Enter Seed (Optional)":"Seed",
                            "Select Week": "Week",
                           })

    ## DATA PRE-PROCESSING TO ENSURE APPROPRIATE VALUES
    df = df.drop_duplicates()

    ## SELECT LATEST ENTRY FOR EACH TEAM FOR EACH WEEK
    latestTimestampIndex = df.groupby(['Week', 'Team'])['Timestamp'].transform(max) == df['Timestamp']
    df = df.loc[latestTimestampIndex]

    ## CREATE NULL ENTRIES IF DATA IS MISSING FOR ANY TEAM/WEEK
    timestampDF = df.pivot(index='Team', columns='Week', values='Timestamp').unstack().reset_index().copy()
    timestampDF = timestampDF.rename(columns={0:'Timestamp'})

    multiplayerDF = df.pivot(index='Team', columns='Week', values='Multiplayer').unstack().reset_index().copy()
    multiplayerDF = multiplayerDF.rename(columns={0:'Multiplayer'})

    seedDF = df.pivot(index='Team', columns='Week', values='Seed').unstack().reset_index().copy()
    seedDF = seedDF.rename(columns={0:'Seed'})

    # MERGE TIMESTAMP, MULTIPLAYER, SEED
    temp1 = timestampDF.merge(multiplayerDF, left_on=['Week', 'Team'], right_on=['Week', 'Team'], how='left')
    outputDF = temp1.merge(seedDF, left_on=['Week', 'Team'], right_on=['Week', 'Team'], how='left')

    ### ToDo - Verify if player entered before kickoff time ###

    return outputDF

def getMultipliers(sheetsDF, origMultiplierList, fillNullValue=1234):
    # ToDo: Complete function docstring
    
    ### CONVERT INFO TO SEEDS DF
    seedsDF = sheetsDF.pivot(index='Team', columns='Week', values='Seed')
    seedsDF = seedsDF.fillna(value=fillNullValue)

    ### CONVERT SEEDS TO MULTIPLIERS
    multiplierDict = {}
    for team in list(seedsDF.index):
        multiplierList = origMultiplierList.copy()

        #### ToDo: INSERT FUNCTION TO SCRAMBLE SEEDS HERE
        teamSeeds = list(seedsDF.loc[team])

        teamMultipliers = []
        for seed in teamSeeds:
            random.seed(seed)
            multiplier = random.choice(multiplierList)
            multiplierList.remove(multiplier)
            teamMultipliers.append(multiplier)
        multiplierDict[team] = teamMultipliers
        multiplierDF = pd.DataFrame.from_dict(multiplierDict, orient='index', columns=seedsDF.columns)

        # Reverse Pivot to get dimensions of Team/Week per row
        unstacked_multiplierDF = multiplierDF.unstack().reset_index().copy()
        unstacked_multiplierDF = unstacked_multiplierDF.rename(columns={'level_1':'Team', 0:'Multiplier'})
        #unstacked_multiplierDF['Select Week'] = unstacked_multiplierDF['Select Week'].apply(lambda x: x.split(' ')[1])
    return multiplierDF, unstacked_multiplierDF
