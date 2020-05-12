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

############## ToDo - Write to Google Sheets Class ##############
def getSheetsData(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME, fillNullValue=np.nan):
    '''
    Wrapper function for reading Google Sheets data into Pandas DataFrame
    :param SAMPLE_SPREADSHEET_ID (str): Google Sheet ID. For additional documentation see: https://developers.google.com/sheets/api/quickstart/python
    :param SAMPLE_RANGE_NAME (str): A1 Notation cell range to read from Google Sheet. See: https://developers.google.com/sheets/api/quickstart/python
    :param fillNullValue: Value to fill null spreadsheet cells with. (Default = np.nan)
    :return (DataFrame): Pandas DataFrame representing data from Google Sheet
    '''

    #### CALL SHEET API
    if os.path.exists('credentials/token.pickle'):
            with open('credentials/token.pickle', 'rb') as token:
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

    ##### TRANSFORMATIONS TO SHEETS DATA #####
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
    outputDF['Week'] = outputDF['Week'].apply(lambda x: int(x.split(' ')[1]))

    ### ToDo - Verify if player entered before kickoff time ###

    return outputDF

def writeSheetData(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME, values):
    '''
    [ TO BE COMPLETED ]
    :param SAMPLE_SPREADSHEET_ID (str): Google Sheet ID. For additional documentation see: https://developers.google.com/sheets/api/quickstart/python
    :param SAMPLE_RANGE_NAME (str): A1 Notation cell range to read from Google Sheet. See: https://developers.google.com/sheets/api/quickstart/python
    :param values: [ TO BE COMPLETED ]
    '''

    body = {'values': values}

    if os.path.exists('credentials/token.pickle'):
        with open('credentials/token.pickle', 'rb') as token:
            creds = pickle.load(token)

    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()

    service.spreadsheets().values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                       range=SAMPLE_RANGE_NAME,
                                       valueInputOption='RAW',
                                       body=body).execute()

    return 1

def getMultipliers(sheetsDF, origMultiplierList, fillNullValue=1234):
    '''
    [TO BE COMPLETED]
    :param sheetsDF (DataFrame): [TO BE COMPLETED]
    :param origMultiplierLis (list): [TO BE COMPLETED]
    :param fillNullValue (int): Default seed value if none provided (Default = 1234)
    :return: [TO BE COMPLETED]
    '''

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


############## ToDo - Write to ESPN Class ##############
def getTeamsKey(leagueID, year, swid_cookie, s2_cookie):
    '''
    Get list of Teams and Team ID from ESPN Fantasy Football API. Create Team Name as {Location} + {Nickname} + ({Abbreviation})
    :param leagueID (str): ESPN League ID. For further information on ESPN Parameters, see here: https://stmorse.github.io/journal/espn-fantasy-v3.html
    :param year (str): ESPN League Year
    :param swid_cookie (str): ESPN SWID Cookie for private leagues
    :param s2_cookie (str): ESPN S2 Cookie for private leagues
    :return (DataFrame): Nbr Rows = {n Teams}. Cols = [FullTeamName]
    '''
    # ToDo: Complete function docstring

    url = "https://fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{leagueID}?view=mBoxscore".format(
    leagueID=leagueID,
    year=year)

    r = requests.get(url,
                     cookies={"swid": "{swid_cookie}".format(swid_cookie=swid_cookie),
                              "espn_s2": "{s2_cookie}".format(s2_cookie=s2_cookie)})

    teams = pd.DataFrame(r.json()['teams'])
    teams['FullTeamName'] = teams['location'] + " " + teams['nickname'] + " (" + teams['abbrev'] + ")"
    teamsKey = teams[['id', 'FullTeamName']]
    teamsKey = teamsKey.set_index('id')

    ## Error handling for bye's
    teamsKey.loc[-999] = 'BYE'

    return teamsKey

def getCurrentWeek(leagueID, year, swid_cookie, s2_cookie):
    '''
    Get current matchup week from ESPN Fantasy Football API.
    :param leagueID (str): ESPN League ID. For further information on ESPN Parameters, see here: https://stmorse.github.io/journal/espn-fantasy-v3.html
    :param year (str): ESPN League Year
    :param swid_cookie (str): ESPN SWID Cookie for private leagues
    :param s2_cookie (str): ESPN S2 Cookie for private leagues
    :return (int): Current matchup week
    '''

    url = "https://fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{leagueID}?view=mBoxscore".format(
    leagueID=leagueID,
    year=year)

    r = requests.get(url,

             cookies={"swid": "{swid_cookie}".format(swid_cookie=swid_cookie),
                      "espn_s2": "{s2_cookie}".format(s2_cookie=s2_cookie)})
    response = r.json()

    ## FIND CURRENT WEEK NBR
    matchupPeriodId = response['status']['currentMatchupPeriod']

    return matchupPeriodId

def getWeekScoreboard(leagueID, year, swid_cookie, s2_cookie, viewWeek):
    '''
    Get DataFrame of scores by team for a given matchup week.
    :param leagueID (str): ESPN League ID. For further information on ESPN Parameters, see here: https://stmorse.github.io/journal/espn-fantasy-v3.html
    :param year (str): ESPN League Year
    :param swid_cookie (str): ESPN SWID Cookie for private leagues
    :param s2_cookie (str): ESPN S2 Cookie for private leagues
    :param viewWeek (int): Matchup week to pull scores for
    :return (DataFrame): Nbr Rows = {n Teams}. Cols = [Week, matchupID, teamID, Points, home_away]
    '''

    url = "https://fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{leagueID}?view=mBoxscore".format(
    leagueID=leagueID,
    year=year)

    r = requests.get(url,

             cookies={"swid": "{swid_cookie}".format(swid_cookie=swid_cookie),
                      "espn_s2": "{s2_cookie}".format(s2_cookie=s2_cookie)})
    response = r.json()

    ## FIND CURRENT WEEK NBR
    matchupPeriodId = response['status']['currentMatchupPeriod']

    # GET LIST OF GAMES FOR VIEW WEEK
    response_week = [game for game in response['schedule'] if game['matchupPeriodId'] == viewWeek]

    ## Fill Score data for BYE weeks
    for x in range(0,len(response_week)):
        if 'away' not in response_week[x].keys():
            response_week[x]['away'] = {'teamId': -999, 'totalPoints': 0, 'rosterForCurrentScoringPeriod':{'appliedStatTotal': 0}}
        if 'home' not in response_week[x].keys():
            response_week[x]['home'] = {'teamId': -999, 'totalPoints': 0, 'rosterForCurrentScoringPeriod':{'appliedStatTotal': 0}}

    gameList = []

    for game in response_week:
        gameID = game['id']
        week = game['matchupPeriodId']

        home_teamID = game['home']['teamId']
        away_teamID = game['away']['teamId']

        # JSON output Format depends on Week
        if week < matchupPeriodId: # Past Week
            home_pts = game['home']['totalPoints']
            away_pts = game['away']['totalPoints']
        elif week == matchupPeriodId: # Current Week
            try:
                home_pts = game['home']['rosterForCurrentScoringPeriod']['appliedStatTotal']
                away_pts = game['away']['rosterForCurrentScoringPeriod']['appliedStatTotal']
            except KeyError: # Support API after season is over (when scores finalized but matchup week not iterated)
                home_pts = game['home']['totalPoints']
                away_pts = game['away']['totalPoints']
        elif week > matchupPeriodId: # Future Week
            home_pts = 0
            away_pts = 0

        gameList.append([gameID, week, home_teamID, away_teamID, home_pts, away_pts])

    scoreboardDF = pd.DataFrame(gameList, columns=['id', 'Week', 'home_teamID', 'away_teamID', 'home_pts', 'away_pts'])
    scoreboardDF['matchupID'] = ((scoreboardDF['id'] % (6)) + 1)

    ## BREAK OUT HOME/AWAY TEAMS TO SINGLE COLUMN
    home_df = scoreboardDF[['Week', 'matchupID', 'home_teamID', 'home_pts']].copy()
    home_df['home_away'] = 'Home'
    home_df = home_df.rename(columns={'home_teamID':'teamID', 'home_pts':'Points'})

    away_df = scoreboardDF[['Week', 'matchupID', 'away_teamID', 'away_pts']].copy()
    away_df['home_away'] = 'Away'
    away_df = away_df.rename(columns={'away_teamID':'teamID', 'away_pts':'Points'})

    scoreboardDF = home_df.append(away_df)

    return scoreboardDF

def getWeekPlayerScores(leagueID, year, swid_cookie, s2_cookie, viewWeek):
    '''
    Get DataFrame of individual player scores for all rostered players
    :param leagueID (str): ESPN League ID. For further information on ESPN Parameters, see here: https://stmorse.github.io/journal/espn-fantasy-v3.html
    :param year (str): ESPN League Year
    :param swid_cookie (str): ESPN SWID Cookie for private leagues
    :param s2_cookie (str): ESPN S2 Cookie for private leagues
    :param viewWeek (int): Matchup week to pull scores for
    :return (DataFrame): Nbr Rows = {n Teams * nbr Players / Team}. Cols = [Week, Team ID, Player, Slot, Pos, Status, Proj, Actual]
    '''

    ## Define dictionary of lineup slot codes to parse JSON
    slotcodes = {
        0 : 'QB', 2 : 'RB', 4 : 'WR',
        6 : 'TE', 16: 'Def', 17: 'K',
        20: 'Bench', 21: 'IR', 23: 'Flex', 18: 'P'
    }

    url = 'https://fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{leagueID}?view=mMatchup&view=mMatchupScore'.format(
        year=year,
        leagueID=leagueID)

    data = []
    print('Week ', end='')
    print(viewWeek, end=' ')

    r = requests.get(url,
                 params={'scoringPeriodId': viewWeek},
                 cookies={"SWID": swid_cookie, "espn_s2": s2_cookie})
    d = r.json()

    for tm in d['teams']:
        tmid = tm['id']
        for p in tm['roster']['entries']:
            name = p['playerPoolEntry']['player']['fullName']
            slot = p['lineupSlotId']
            pos  = slotcodes[slot]

            # injured status (need try/exc bc of D/ST)
            inj = 'NA'
            try:
                inj = p['playerPoolEntry']['player']['injuryStatus']
            except:
                pass

            # projected/actual points
            proj, act = None, None
            for stat in p['playerPoolEntry']['player']['stats']:
                if stat['scoringPeriodId'] != viewWeek:
                    continue
                if stat['statSourceId'] == 0:
                    act = stat['appliedTotal']
                elif stat['statSourceId'] == 1:
                    proj = stat['appliedTotal']

            data.append([
                viewWeek, tmid, name, slot, pos, inj, proj, act
            ])
    print('\nComplete.')

    data = pd.DataFrame(data,
                        columns=['Week', 'Team ID', 'Player', 'Slot',
                                 'Pos', 'Status', 'Proj', 'Actual'])
    return data

def mergeScores(teamsDF, scoreboardDF, multiplierDF, playerScoresDF):
    '''
    [TO BE COMPLETED]
    :param teamsDF (DataFrame):  Nbr Rows = {n Teams}. Cols = [FullTeamName]
    :param scoreboardDF (DataFrame): Nbr Rows = {n Teams}. Cols = [Week, matchupID, teamID, Points, home_away]
    :param multiplierDF (DataFrame): Nbr Rows = {n Teams}. Cols = [ TO BE COMPLETED ]
    :param playerScoresDF (DataFrame): Nbr Rows = {n Teams * nbr Players / Team}. Cols = [Week, Team ID, Player, Slot, Pos, Status, Proj, Actual]
    :return (DataFrame): Nbr Rows = {n Teams}. Cols = [TO BE COMPLETED]
    '''

    df = scoreboardDF.merge(teamsDF, left_on='teamID', right_index=True, how='left')
    df = df.merge(multiplierDF, left_on=['Week', 'FullTeamName'], right_on=['Week', 'Team'], how='left')
    df = df.merge(playerScoresDF, left_on=['Week', 'teamID', 'Multiplayer'], right_on=["Week", 'Team ID', 'Player'], how='left')
    df = df[['Week', 'matchupID','home_away', 'Points', 'FullTeamName', 'Timestamp', 'Multiplayer', 'Multiplier', 'Actual']]

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
