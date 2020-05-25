### CONFIG.PY Definied for use in Input.py web form
# ToDo - merge config.txt into here
import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
