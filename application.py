from flask import Flask, render_template, redirect, flash, url_for, request, session
import datetime
import requests
import configparser
import sys,os,os.path
import pickle
import pandas as pd
import numpy as np
import random
import boto3
from boto3.dynamodb.conditions import Key
import math

import helpers as helpers
import colors as colors
from config import Config
from forms import InputForm
from espn import espn

application = Flask(__name__)
application.config.from_object(Config)

################################################################################
##  ******************* GET CONFIG INFO *******************
################################################################################

# League Parameters
multiplierList = Config.multiplierList

################################################################################
##  ******************* GET DATA FROM ESPN/AWS *******************
################################################################################

initialTime=datetime.datetime.now()

## Instantiate ESPN FF class object
espn_stats = espn(Config.leagueID, Config.year, Config.swid_cookie, Config.s2_cookie)
teamsDF = espn_stats.getTeamsKey()

# Define AWS DynamoDB Resources
dynamodb = boto3.resource('dynamodb', region_name=Config.region_name)
multiplayer = dynamodb.Table('multiplayer_input')
teams = dynamodb.Table('teams')
multiplier = dynamodb.Table('multiplier_input')

################################################################################
##  ******************* RENDER PAGES WITH FLASK *******************
################################################################################

@application.route('/')
def home():
    return redirect('/scoreboard')

@application.route('/scoreboard')
def scoreboard_page():
    ## Find current week and redirect to there
    currentWeek = espn_stats.getCurrentWeek()
    currentWeek = str(currentWeek)

    return redirect('/scoreboard/week{}'.format(currentWeek))

### Generic routing function to cover each week
@application.route('/scoreboard/week<viewWeek>')
def weekGeneric_page(viewWeek):

    viewWeek = int(viewWeek)

    # GET TEAM SCORES FOR WEEK - (BASE)
    scoreboardDF = espn_stats.getWeekScoreboard(viewWeek)
    scoreboardDF = scoreboardDF.merge(teamsDF, left_on='teamID', right_index=True, how='left')
    scoreboardDF = scoreboardDF.rename(columns={'FullTeamName':'Team'})

    # LOOKUP MULTIPLIER (BY WEEK/TEAM ID)
    # Pull Multiplier from AWS
    scoreboardDF['Multiplier'] = scoreboardDF['teamID'].apply(lambda x: float(multiplier.get_item(Key={'week':str(viewWeek), 'teamID':str(x)})['Item']['Multiplier']))

    # LOOK UP MULTIPLAYER (BY WEEK/TEAM ID) VIA AWS DYNAMO DB QUERY
    scoreboardDF['Multiplayer'] = scoreboardDF['teamID'].apply(lambda x:
        multiplayer.get_item(Key={'week':int(viewWeek), 'team':str(x)})
        .get('Item', {})
        .get('multiplayer'))

    # GET PLAYER SCORES FOR WEEK (AND APPEND)
    playerScoresDF = espn_stats.getWeekPlayerScores(viewWeek)

    # JOIN
    adjustedScores = helpers.mergeScores(teamsDF, scoreboardDF, playerScoresDF)
    adjustedScores = adjustedScores.round({'Actual':2, 'Adjustment':2, 'AdjustedScore':2}) # Round for scoreboard appearance
    scoreboardDict = helpers.scoresToDict(adjustedScores, int(teamsDF.shape[0]/2))

    print(scoreboardDict.keys())
    return render_template('scoreboard.html',
                            input1='Week {}'.format(viewWeek),
                            scoreboardDict=scoreboardDict, # Team, Multiplayer, Multiplier, Score Adjustment, Adjusted Score
                            time=datetime.datetime.now())

@application.route('/MultiplierResults')
def multiplier_page():

    # Get current week
    currentWeek = espn_stats.getCurrentWeek()

    # Map Multipliers to Gradient colors - Create dictionary key
    list_len = len(Config.multiplierList)
    gradient1_len = math.floor((list_len + 1) / 2)
    gradient2_len = list_len + 1 - gradient1_len
    gradient1 = colors.linear_gradient(start_hex="#ff0000", finish_hex="#ffffff", n=gradient1_len)['hex'] # Red -> White
    gradient2 = colors.linear_gradient(start_hex="#ffffff", finish_hex="#008000", n=gradient2_len)['hex'] # White -> Green

    color_gradient = []
    for i in gradient1 + gradient2:
        if i not in color_gradient:
            color_gradient.append(i)

    multiplier_list = [str(x) for x in Config.multiplierList]
    color_dict = dict(zip(multiplier_list, color_gradient))

    # Create dict of past multipliers for each team
    multiplier_dict = {}

    for id in teamsDF.index:
        if id != -999:
            # Get tuples of (week, multiplier)
            response = multiplier.scan(FilterExpression=Key('teamID').eq(str(id)))
            multiplier_history = [(int(x['week']), x['Multiplier']) for x in response['Items']]
            multiplier_history.sort(key=lambda x: int(x[0]))
            #print(multiplier_history)

            # Add list of past multipliers to dict
            multiplier_dict[teamsDF.loc[id]['FullTeamName']] = multiplier_history

    return render_template('multiplier_results.html',
                            multiplier_dict=multiplier_dict,
                            color_dict=color_dict,
                            currentWeek=currentWeek,
                            time=datetime.datetime.now())


@application.route('/input_form', methods=['GET', 'POST'])
def input_form():
    # If user is authenticated, expose form
    if 'username' in session:
        print(session['username'])
        form = InputForm()
        if form.validate_on_submit():
            flash('Submission: multiplayer={}'.format(form.multiplayer.data))
            # Write to DynamoDB

            currentWeek = 10 # TEMPORARY ToDo: Pull this from current Week

            # Get teamID
            teamID = teams.get_item(Key={'username':session['username']})['Item']['teamID']

            # Check if existing entry not in play and submission not in play. ToDo - Error handling if no entry
            existing_multiplayer = multiplayer.get_item(Key={'week':currentWeek, 'team':teamID})['Item']['multiplayer']

            if espn_stats.getPlayerLockStatus(existing_multiplayer) == False:
                if espn_stats.getPlayerLockStatus(form.multiplayer.data) == False: # Success
                    # ToDo - Check that player is on roster?
                    # Write new multiplayer - ToDo - error handling
                    multiplayer.put_item(Item={'week':currentWeek, 'team':teamID, 'seed':'123', 'multiplayer':form.multiplayer.data})

                    # write multiplier
                    helpers.updateMultiplier(currentWeek=currentWeek, teamID=teamID, multiplier_db_table=multiplier)

                    return render_template('submission_success.html', username=session['username'], time=datetime.datetime.now())
                else:
                    return render_template('submission_fail.html', username=session['username'], time=datetime.datetime.now(), error='Multiplayer entry is not valid')
            else:
                return render_template('submission_fail.html', username=session['username'], time=datetime.datetime.now(), error='Existing multiplayer entry is already locked')

        return render_template('input_form.html', form=form, username=session['username']) # ToDo - Clean up this section

    else: # Route to Cognito UI
        print('Not Authenticated')
        return redirect(url_for('authenticate'))

############ ROUTING FOR COGNITO LOGIN ##############
# Route to Cognito UI
@application.route('/auth')
def authenticate():
    # AWS Cognito
    return redirect("{cognito_url}/login?response_type=code&client_id={app_client_id}&redirect_uri={redirect_uri}"\
            .format(cognito_url=Config.cognito_url, app_client_id=Config.app_client_id, redirect_uri=Config.redirect_uri))

# Return from Cognito UI - Add username to session
@application.route('/input_form_cognito', methods=['GET', 'POST'])
def cognito_response():
    access_code = request.args.get('code')

    # Convert Access code to Token via TOKEN endpoint
    # Reference: exchange_code_for_token function https://github.com/cgauge/Flask-AWSCognito/tree/6882a0c246dcc8da8e299c1e8b468ef5899bc373
    domain = Config.cognito_url
    token_url = "{}/oauth2/token".format(domain)
    data = {
                "code": access_code,
                "redirect_uri": Config.redirect_uri,
                "client_id": Config.app_client_id,
                "grant_type": "authorization_code",
            }
    headers = {} # Add b64 encoded client id : client secret here if needed
    requests_client = requests.post

    response = requests_client(token_url, data=data, headers=headers)
    access_token = response.json()['access_token']

    # Convert Token to User Info via Boto
    cognito_client = boto3.client('cognito-idp')
    user_info = cognito_client.get_user(AccessToken=access_token)
    session['username'] = user_info['Username']
    print("Authenticated Username: {}".format(session['username']))

    return redirect(url_for('input_form'))

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = False
    application.run()
