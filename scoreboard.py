from flask import Flask, render_template
import datetime
import requests
import helpers as helpers

import sys,os,os.path

app = Flask(__name__)


@app.route('/')
def week1_page():

  # Python code would go here

  return render_template('scoreboard.html',
                        input1='Week 1',
                        input2='Input 2',
                        time=datetime.datetime.now())

@app.route('/Week2')
def week2_page():

  # Python code would go here

  return render_template('scoreboard.html',
                        input1='Week 2',
                        input2='Input 2',
                        time=datetime.datetime.now())
