from flask import Flask, render_template, redirect, flash, url_for, request
import datetime
import requests
import configparser
import sys,os,os.path
import pickle
import pandas as pd
import numpy as np
import random

import helpers as helpers
from config import Config
from forms import InputForm
from espn import espn

app = Flask(__name__)
app.config.from_object(Config)

################################################################################
##  ******************* GET CONFIG INFO *******************
################################################################################
config = configparser.RawConfigParser()
config.read('config.txt')

# League Parameters
multiplierList = [float(x) for x in config.get('League Parameters', 'multiplierList').split(', ')]

# ESPN Parameters
# Imported from config

################################################################################
##  ******************* GET DATA FROM GOOGLE/ESPN *******************
################################################################################

initialTime=datetime.datetime.now()

##  ******************* PULL MATCHUPS AND SCORING FROM ESPN *******************
## ******************* INSTANTIATE ESPN FF CLASS OBJECT *******************
espn_stats = espn(Config.leagueID, Config.year, Config.swid_cookie, Config.s2_cookie)

# ToDo - logic to map native username to teamID
teamsDF = espn_stats.getTeamsKey()
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

    # LOOK UP MULTIPLAYER (BY WEEK/TEAM ID)
    # Simulate Update via API - ToDo: Replace with DynamoDB Read API
    multiplayer_df = pd.read_csv('sample_data/multiplayer_input.csv')
    multiplayers = multiplayer_df.set_index(['Week', 'TeamID']).to_dict(orient='index')
    scoreboardDF['Multiplayer'] = scoreboardDF['teamID'].apply(lambda x: multiplayers[(viewWeek, x)]['Multiplayer'])

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
    form = InputForm()
    if form.validate_on_submit():
        flash('Submission: user {}, multiplayer={}, seed={}'.format(
            form.username.data, form.multiplayer.data, form.seed.data))
        # ToDo - Write to DynamoDB
        return redirect(url_for('temp_redirect'))
    return render_template('input_form.html', title='Sign In', form=form)

@app.route('/temp_redirect')
def temp_redirect():
    return render_template('temp_redirect.html')

@app.route('/auth')
def authenticate():
    # AWS Cognito - https://ffl.auth.us-east-2.amazoncognito.com/login?response_type=code&client_id=6n7h391ts8jlt89pied1milh5a&redirect_uri=http://localhost:5000/auth/
    return redirect("https://ffl.auth.us-east-2.amazoncognito.com/login?response_type=code&client_id=6n7h391ts8jlt89pied1milh5a&redirect_uri=http://localhost:5000/input_form_cognito")


@app.route('/input_form_cognito')
def cognito_response():
    code = request.args.get('code')
    print(code)
    # Convert code to JWT
    # Get User
    # Expose form?
    return render_template('temp_redirect.html')
