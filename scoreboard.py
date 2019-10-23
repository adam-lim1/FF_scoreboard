from flask import Flask, render_template
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

@app.route('/')
def week1_page():
    viewWeek = 1

    # GET SHEETS INPUT

    # GET TEAM SCORES FOR WEEK
    scoreboardDF = helpers.getWeekScoreboard(leagueID, year, swid_cookie, s2_cookie, viewWeek)
    scoreboardDF = scoreboardDF.merge(teamsDF, left_on='teamID', right_index=True, how='left')
    scoreboardDF = scoreboardDF.rename(columns={'FullTeamName':'Team'})

    # GET PLAYER SCORES FOR WEEK
    playerScoresDF = helpers.getWeekPlayerScores(leagueID, year, swid_cookie, s2_cookie, viewWeek)
    # JOIN

    # Python code would go here

    ### GET DICT OF SCORES
    scoreboardDict = {}

    for game in range(1,6+1):
        matchupDict = {}
        for home_away in ["Home", "Away"]:
            teamDict = {
                'Team': scoreboardDF.query('matchupID == {}'.format(game)).query('home_away=="{}"'.format(home_away))['Team'].values[0],
                'Points': scoreboardDF.query('matchupID == {}'.format(game)).query('home_away=="{}"'.format(home_away))['Points'].values[0]
            }
            matchupDict[home_away] = teamDict
        scoreboardDict[game] = matchupDict

    return render_template('scoreboard.html',
                            input1=initialTime,
                            input2='Input 2',
                            scoreboardDict=scoreboardDict,
                            time=datetime.datetime.now())

@app.route('/Week2')
def week2_page():

    # Python code would go here

    return render_template('scoreboard.html',
                            input1='Week 2',
                            input2='Input 2',
                            time=datetime.datetime.now())

@app.route('/Week3')
def week3_page():

    # Python code would go here

      return render_template('scoreboard.html',
                            input1='Week 3',
                            input2='Input 2',
                            time=datetime.datetime.now())
@app.route('/Week4')
def week4_page():

    # Python code would go here

      return render_template('scoreboard.html',
                            input1='Week 4',
                            input2='Input 2',
                            time=datetime.datetime.now())

@app.route('/Week5')
def week5_page():

    # Python code would go here

      return render_template('scoreboard.html',
                            input1='Week 5',
                            input2='Input 2',
                            time=datetime.datetime.now())

@app.route('/Week6')
def week6_page():

    # Python code would go here

      return render_template('scoreboard.html',
                            input1='Week 6',
                            input2='Input 2',
                            time=datetime.datetime.now())
@app.route('/Week7')
def week7_page():

    # Python code would go here

      return render_template('scoreboard.html',
                            input1='Week 7',
                            input2='Input 2',
                            time=datetime.datetime.now())
@app.route('/Week8')
def week8_page():

    # Python code would go here

      return render_template('scoreboard.html',
                            input1='Week 8',
                            input2='Input 2',
                            time=datetime.datetime.now())

@app.route('/Week9')
def week9_page():

    # Python code would go here

      return render_template('scoreboard.html',
                            input1='Week 9',
                            input2='Input 2',
                            time=datetime.datetime.now())
@app.route('/Week10')
def week10_page():

    # Python code would go here

      return render_template('scoreboard.html',
                            input1='Week 10',
                            input2='Input 2',
                            time=datetime.datetime.now())
@app.route('/Week11')
def week11_page():

    # Python code would go here

      return render_template('scoreboard.html',
                            input1='Week 11',
                            input2='Input 2',
                            time=datetime.datetime.now())

@app.route('/Week12')
def week12_page():

    # Python code would go here

      return render_template('scoreboard.html',
                            input1='Week 12',
                            input2='Input 2',
                            time=datetime.datetime.now())
@app.route('/Week13')
def week13_page():

    # Python code would go here

      return render_template('scoreboard.html',
                            input1='Week 13',
                            input2='Input 2',
                            time=datetime.datetime.now())

@app.route('/Week14')
def week14_page():

    # Python code would go here

      return render_template('scoreboard.html',
                            input1='Week 14',
                            input2='Input 2',
                            time=datetime.datetime.now())

@app.route('/Week15')
def week15_page():

    # Python code would go here

      return render_template('scoreboard.html',
                            input1='Week 15',
                            input2='Input 2',
                            time=datetime.datetime.now())
@app.route('/Week16')
def week16_page():

    # Python code would go here

      return render_template('scoreboard.html',
                            input1='Week 16',
                            input2='Input 2',
                            time=datetime.datetime.now())
@app.route('/Week17')
def week17_page():

    # Python code would go here

      return render_template('scoreboard.html',
                            input1='Week 17',
                            input2='Input 2',
                            time=datetime.datetime.now())
