from dataclasses import field
from user.forme import KarticaForm
from wtforms import StringField, PasswordField, SubmitField,IntegerField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from flask_wtf import FlaskForm

class UplataForm(KarticaForm):
    stanje=IntegerField(label='Iznos:  ', validators=[DataRequired()])
    submit = SubmitField(label='Uplata')