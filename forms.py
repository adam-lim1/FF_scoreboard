from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired

class InputForm(FlaskForm):
    # username = StringField('Username', validators=[DataRequired()])
    multiplayer = StringField('Multiplayer', validators=[DataRequired()])
    # seed = IntegerField('Multiplier Seed', default=42)
    submit = SubmitField('Submit')
