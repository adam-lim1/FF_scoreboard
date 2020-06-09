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

import helpers as helpers
from config import Config
from forms import InputForm
from espn import espn

app = Flask(__name__)
app.config.from_object(Config)

################################################################################
##  ******************* GET CONFIG INFO *******************
################################################################################

# League Parameters
multiplierList = Config.multiplierList

################################################################################
##  ******************* GET DATA FROM GOOGLE/ESPN *******************
################################################################################

initialTime=datetime.datetime.now()

## ******************* INSTANTIATE ESPN FF CLASS OBJECT *******************
espn_stats = espn(Config.leagueID, Config.year, Config.swid_cookie, Config.s2_cookie)
teamsDF = espn_stats.getTeamsKey()

# Define AWS DynamoDB Resources
dynamodb = boto3.resource('dynamodb', region_name=Config.region_name)
multiplayer = dynamodb.Table('multiplayer_input')
teams = dynamodb.Table('teams')
# ToDo - Define multiplier table

################################################################################
##  ******************* RENDER PAGES WITH FLASK *******************
################################################################################

@app.route('/')
def home():
    return redirect('/scoreboard')

@app.route('/scoreboard')
def scoreboard_page():
    ## Find current week and redirect to there
    currentWeek = espn_stats.getCurrentWeek()
    currentWeek = str(currentWeek)

    return redirect('/scoreboard/week{}'.format(currentWeek))

### Generic routing function to cover each week
@app.route('/scoreboard/week<viewWeek>')
def weekGeneric_page(viewWeek):

    viewWeek = int(viewWeek)

    # GET TEAM SCORES FOR WEEK - (BASE)
    scoreboardDF = espn_stats.getWeekScoreboard(viewWeek)
    scoreboardDF = scoreboardDF.merge(teamsDF, left_on='teamID', right_index=True, how='left')
    scoreboardDF = scoreboardDF.rename(columns={'FullTeamName':'Team'})

    # LOOKUP MULTIPLIER (BY WEEK/TEAM ID)
    # Simulate Update via API - ToDo: Replace with DynamoDB Read API
    # ToDo - Need to handle if player doesn't make entry (nulls)
    multiplier_df = pd.read_csv('sample_data/multipliers.csv')
    multipliers = multiplier_df.set_index(['Week', 'TeamID']).to_dict(orient='index')
    scoreboardDF['Multiplier'] = scoreboardDF['teamID'].apply(lambda x: multipliers[(viewWeek, x)]['Multiplier'])
    # ToDo - Pull Multiplier from AWS

    # LOOK UP MULTIPLAYER (BY WEEK/TEAM ID) VIA AWS DYNAMO DB QUERY
    scoreboardDF['Multiplayer'] = scoreboardDF['teamID'].apply(lambda x: multiplayer.get_item(Key={'week':int(viewWeek), 'team':str(x)})['Item']['multiplayer'])

    # GET PLAYER SCORES FOR WEEK (AND APPEND)
    playerScoresDF = espn_stats.getWeekPlayerScores(viewWeek)

    # JOIN
    adjustedScores = helpers.mergeScores(teamsDF, scoreboardDF, playerScoresDF)
    scoreboardDict = helpers.scoresToDict(adjustedScores, int(teamsDF.shape[0]/2))

    print(scoreboardDict.keys())
    return render_template('scoreboard.html',
                            input1='Week {}'.format(viewWeek),
                            scoreboardDict=scoreboardDict, # Team, Multiplayer, Multiplier, Score Adjustment, Adjusted Score
                            time=datetime.datetime.now())

@app.route('/MultiplierResults')
def multiplier_page():

    # ToDo - Treatment to not reval multiplier if gametime has not yet passed

    return render_template('multipliers_GS.html',
                            time=datetime.datetime.now())


@app.route('/input_form', methods=['GET', 'POST'])
def input_form():
    # If user is authenticated, expose form
    if 'username' in session:
        print(session['username'])
        form = InputForm()
        if form.validate_on_submit():
            flash('Submission: multiplayer={}'.format(form.multiplayer.data))
            # Write to DynamoDB

            viewWeek = 10 # TEMPORARY ToDo: Pull this from current Week

            # Get teamID - ToDo: error handling if username not in DB
            teamID = teams.scan(FilterExpression=Key('username').eq(session['username']))['Items'][0]['teamID']

            # ToDo - Check if existing entry not in play and submission not in play
            existing_multiplayer = multiplayer.get_item(Key={'week':viewWeek, 'team':teamID})['Item']['multiplayer']

            if espn_stats.getPlayerLockStatus(existing_multiplayer) == False:
                if espn_stats.getPlayerLockStatus(form.multiplayer.data) == False:
                    # Success
                    # Write new multiplier - ToDo - error handling
                    multiplayer.put_item(Item={'week':viewWeek, 'team':teamID, 'seed':'123', 'multiplayer':form.multiplayer.data})

                    return render_template('submission_success.html', username=session['username'], time=datetime.datetime.now()
            else:
                # multiplayer not valid
                print('error - not valid')
                )


            return render_template('temp_redirect.html', username=session['username']) #redirect(url_for('temp_redirect'))
        return render_template('input_form.html', form=form, username=session['username']) # ToDo - Clean up this section

    else: # Route to Cognito UI
        print('Not Authenticated')
        return redirect(url_for('authenticate'))

# HTML landing page after input validated
@app.route('/temp_redirect')
def temp_redirect():
    return render_template('temp_redirect.html')

############ ROUTING FOR COGNITO LOGIN ##############
# Route to Cognito UI
@app.route('/auth')
def authenticate():
    # AWS Cognito
    return redirect("{cognito_url}/login?response_type=code&client_id={app_client_id}&redirect_uri={redirect_uri}"\
            .format(cognito_url=Config.cognito_url, app_client_id=Config.app_client_id, redirect_uri=Config.redirect_uri))

# Return from Cognito UI - Add username to session
@app.route('/input_form_cognito', methods=['GET', 'POST'])
def cognito_response():
    access_code = request.args.get('code')

    # Convert Access code to Token via TOKEN endpoint
    # Reference: exchange_code_for_token function https://github.com/cgauge/Flask-AWSCognito/tree/6882a0c246dcc8da8e299c1e8b468ef5899bc373
    # ToDo - add these to AWS class/Parameters
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
