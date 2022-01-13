from werkzeug.utils import redirect
from user import *
from user.forme import KarticaForm, LoginForm, RegisterForm, ChangeForm
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



@user.route('/change', methods=['GET', 'POST'])
def change_user():
    form = ChangeForm()
    if 'user' in session:
        if request.method == "POST":
            if form.validate_on_submit():
                user=User(form.ime.data,form.prezime.data,form.adresa.data,form.grad.data,form.drzava.data,form.telefon.data,form.email.data,form.password1.data)
                user.email = session['user']['email'] 
                user.id = session['user']['id']
                data=UserSchema().dump(user)
                data = jsonify(data).get_data()
                zahtev = req.Request("http://localhost:5000/change_user")
                zahtev.add_header('Content-Type', 'application/json; charset=utf-8')
                zahtev.add_header('Content-Length', len(data))
                try:
                    ret = req.urlopen(zahtev, data)
                except HTTPError as e:
                    flash(e.read().decode(),category='danger')
                    return render_template('change.html', form=form)

                user=json.loads(ret.read())
                session["user"]=user
                flash(f"Uspesno ste promenili korisnicke podatke! ",category='primary')
                return redirect(url_for("index"))
            if form.errors != {}:
                for msg in form.errors.values():
                    flash(msg.pop(), category='danger')

                return render_template('change.html', form=form)
        if request.method == 'GET':
            user = session['user']
            form.ime.data = user['ime']
            form.prezime.data = user['prezime']
            form.grad.data = user['grad']
            form.adresa.data = user['adresa']
            form.drzava.data = user['drzava']
            form.telefon.data = user['telefon']
            form.email.data = user['email']

            return render_template('change.html', form=form)

    else:
        return redirect(url_for('user.login'))

@user.route('/stanja', methods=['GET'])
def stanja():
    if 'user' in session:
        return render_template('stanja.html', stanja=session['user']['stanja'])
    else:
        return redirect(url_for('user.login'))

@user.route('/verifikacija',methods=['GET','POST'])
def verifikacija():
    form = KarticaForm()
    if 'user' in session:
        if request.method == "POST":
            if form.validate_on_submit():
                data={"ime":form.ime.data,"brojKartice":form.brojKartice.data,"datumIsteka":form.datumIsteka.data,"kod":form.kod.data,"email":session["user"]['email']} 
                data = jsonify(data).get_data()
                zahtev = req.Request("http://localhost:5000/verifikacija")
                zahtev.add_header('Content-Type', 'application/json; charset=utf-8')
                zahtev.add_header('Content-Length', len(data))
                try:
                    ret = req.urlopen(zahtev, data)

                except HTTPError as e:
                    flash(e.read().decode(),category='danger')
                    return redirect(url_for("index"))

                flash(ret.read().decode(),category='primary')
                return redirect(url_for("index"))
            if form.errors != {}:
                for msg in form.errors.values():
                    flash(msg.pop(), category='danger')

            return render_template('kartica.html', form=form)
        else :
                return render_template('kartica.html', form=form)
    else:
        return redirect(url_for('user.login'))
               
