from dataclasses import field
from user.forme import KarticaForm
from wtforms import StringField, PasswordField, SubmitField,IntegerField, SelectField, FloatField ,HiddenField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from flask_wtf import FlaskForm

class UplataForm(KarticaForm):
    stanje=IntegerField(label='Iznos:  ', validators=[DataRequired()])
    submit = SubmitField(label='Uplata')

class PrenosForm(FlaskForm):
    primalac = StringField(label="Primalac: ", validators=[Email("Email nije ispravan!"), DataRequired()])
    valuta = SelectField(label="Valuta: ", validators=[DataRequired()])
    iznos = FloatField(label="Iznos: ", validators=[DataRequired()])
    submit = SubmitField(label="Posalji korisniku")

class PretragaForm(FlaskForm):
    valuta=SelectField(label="Valuta: ")
    stanje=SelectField(label="Stanje: ")
    email=StringField(label="Email: ")
    submit=SubmitField(label="Pretrazi: ")