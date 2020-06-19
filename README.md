# FF_scoreboard
Custom scoreboard view for ESPN fantasy football league

## Getting Started
**Running the Scoreboard Locally**
```
python -m venv ff-venv
source ff-venv/bin/activate
pip install -r requirements.txt
source FLASK_APP=application.py
flask run
```

## AWS Services Required
- Elastic Beanstalk (EC2, S3, etc.)
- DynamoDB
- Cognito

**Initializing DynamoDB Tables w/ Existing Values**
```
python setup/dynamodb_create_multipliers.py
python setup/dynamodb_create_teams.py
python setup/dynamodb_create_table.py
```

## Helpful References
- ESPN Fantasy Football API: https://stmorse.github.io/journal/espn-fantasy-3-python.html
- Translating Cognito Tokens: https://github.com/cgauge/Flask-AWSCognito/tree/6882a0c246dcc8da8e299c1e8b468ef5899bc373
