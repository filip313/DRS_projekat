from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from flask_wtf import FlaskForm
from user.modeli import User
import phonenumbers

class RegisterForm(FlaskForm):

    ime = StringField(label='Ime:  ', validators=[Length(min=2, max=30),DataRequired()])
    prezime = StringField(label='Prezime:  ', validators=[Length(min=2, max=30),DataRequired()])
    adresa = StringField(label='Adresa:  ', validators=[Length(min=2, max=30),DataRequired()])
    grad = StringField(label='Grad:  ', validators=[Length(min=2, max=30),DataRequired()])
    drzava = StringField(label='Drzava:  ', validators=[Length(min=2, max=30),DataRequired()])
    telefon = StringField(label='Telefon:  ', validators=[Length(min=2, max=30),DataRequired()])
    email = StringField(label='Email: ', validators=[Email(),DataRequired()])
    password1 = PasswordField(label='Sifra: ', validators=[Length(min=6),DataRequired()])
    password2 = PasswordField(label='Potvrdi sifru: ', validators=[EqualTo('password1'), DataRequired()])
    submit = SubmitField(label='Registruj se')

    def validate_telefon(self,telefon):
        ret=phonenumbers.parse(telefon,"IN")
        return phonenumbers.is_valid_number(ret)
