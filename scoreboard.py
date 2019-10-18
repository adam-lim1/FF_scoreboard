from flask import Flask, render_template
import datetime
import requests

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
