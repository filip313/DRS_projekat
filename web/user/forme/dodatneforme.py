from numbers import Number
from wtforms import StringField, PasswordField, SubmitField, FloatField, SelectField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from flask_wtf import FlaskForm
import phonenumbers

class KarticaForm(FlaskForm):
    ime = StringField(label='Ime:  ', validators=[Length(min=2, max=30),DataRequired()])
    brojKartice = StringField(label='Broj kartice:  ', validators=[Length(min=16, max=16),DataRequired()])
    datumIsteka = StringField(label='Datum isteka:  ', validators=[Length(min=5, max=5),DataRequired()])
    kod = StringField(label='Sigurnosni kod: ',validators=[Length(min=3,max=3),DataRequired()])
    submit = SubmitField(label='Verifikuj')


class ZamenaForm(FlaskForm):
    kolicina = FloatField(label="Kolicina: ", validators=[DataRequired()])
    valuta_posle = SelectField(label="Valuta: ", validators=[])
    submit = SubmitField(label="Zameni")