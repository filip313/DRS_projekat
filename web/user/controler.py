from werkzeug.utils import redirect
from user import *
from user.forme import LoginForm, RegisterForm
from user.modeli import UserSchema,User,LoginSchema
from urllib import request as req, parse 
import json
from urllib.error import HTTPError

@user.route("/register",methods=["GET","POST"])

def register():
    form=RegisterForm()
    if request.method=='POST':
        if form.validate_on_submit():
            user=User(form.ime.data,form.prezime.data,form.adresa.data,form.grad.data,form.drzava.data,form.telefon.data,form.email.data,form.password1.data)
            data=UserSchema().dump(user)
            data.pop('id')
            data = jsonify(data).get_data()
            zahtev = req.Request("http://localhost:5000/register")
            zahtev.add_header('Content-Type', 'application/json; charset=utf-8')
            zahtev.add_header('Content-Length', len(data))
            try:
                ret = req.urlopen(zahtev, data)
            except HTTPError as e:
                flash(e.read().decode(),category='danger')
                return render_template("register.html",form=form)
            
            flash(ret.read().decode(),category='primary')
            return redirect(url_for("user.login"))
            
        
        if form.errors != {}:
            for msg in form.errors.values():
                flash(msg.pop(), category='danger')

            return render_template('register.html', form=form)
    else :
        return render_template('register.html', form=form)


@user.route("/login", methods=["GET","POST"])

def login():
    form=LoginForm()
    if request.method=="POST":
        if form.validate_on_submit():
            logovanje=LoginSchema().load({"email":form.email.data,"password":form.password.data})
            data = jsonify(logovanje).get_data()
            zahtev = req.Request("http://localhost:5000/login")
            zahtev.add_header('Content-Type', 'application/json; charset=utf-8')
            zahtev.add_header('Content-Length', len(data))
            try:
                ret = req.urlopen(zahtev, data)
            except HTTPError as e:
                 flash(e.read().decode(),category='danger')
                 return render_template("login.html",form=form)

            user=json.loads(ret.read())
            session["user"]=user
            flash(f"Uspesno ste ulogovani kao {user['ime']}",category='primary')
            return redirect(url_for("index"))
        if form.errors != {}:
            for msg in form.errors.values():
                flash(msg.pop(), category='danger')

            return render_template('login.html', form=form)
    else :
        return render_template('login.html', form=form)


@user.route("/logout", methods=["GET"])

def logout():
    if "user" in session:
        session.pop("user") 
        flash("Korisnik uspesno izlogovan!", category='primary')
    
        
    return redirect(url_for("index"))



