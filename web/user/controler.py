from flask import Blueprint,render_template,request,url_for,jsonify
from user.forme import RegisterForm
from user.modeli import UserSchema,User
from urllib import request


user=Blueprint("user",__name__,static_folder="static",template_folder="template")

@user.route("/register",methods=["GET","POST"])

def register():
    if request.method=='POST':
        form=RegisterForm()
        if form.validate_on_submit():
            user=User(form.ime.data,form.prezime.data,form.adresa.data,form.grad.data,form.drzava.data,form.telefon.data,form.email.data,form.password1.data)
            data=jsonify(UserSchema().dump(user))
            request.urlopen("localhost:5000/register",data=data)
    else :
        return "GET"
