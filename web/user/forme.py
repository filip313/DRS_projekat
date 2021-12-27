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
    email = StringField(label='Email: ', validators=[Email('Email nije ispravan!'),DataRequired()])
    password1 = PasswordField(label='Sifra: ', validators=[Length(min=6),DataRequired()])
    password2 = PasswordField(label='Potvrdi sifru: ', validators=[EqualTo('password1', 'Sifre nisu jednake!'), DataRequired()])
    submit = SubmitField(label='Registruj se')

    def validate_telefon(self,telefon_to_verify):
        ret=phonenumbers.parse(telefon_to_verify.data,"IN")
        if phonenumbers.is_valid_number(ret):
            return True
        else:
            raise ValidationError('Format broja telefona nije ispravan!')