from user import *
from user.forme.dodatneforme import *
from user.forme.userforme import *
from user.modeli.usermodeli import *
from user.modeli.transakcijamodel import *
from user.modeli.stanjemodel import *
from urllib import request as req, parse 
import json
from urllib.error import HTTPError
from transakcije import coin

adresa="http://drs-engine.herokuapp.com"

@user.route("/register",methods=["GET","POST"])

def register():
    form=RegisterForm()
    if request.method=='POST':
        if form.validate_on_submit():
            user=User(form.ime.data,form.prezime.data,form.adresa.data,form.grad.data,form.drzava.data,form.telefon.data,form.email.data,form.password1.data)
            data=UserSchema().dump(user)
            data.pop('id')
            data = jsonify(data).get_data()
            zahtev = req.Request(f"{adresa}/register")
            zahtev.add_header('Content-Type', 'application/json; charset=utf-8')
            zahtev.add_header('Content-Length', len(data))
            try:
                ret = req.urlopen(zahtev, data)
            except HTTPError as e:
                flash(e.read().decode(),category='danger')
                return render_template("register.html",form=form, ulogovan=False)
            
            flash(ret.read().decode(),category='primary')
            return redirect(url_for("user.login"))
            
        
        if form.errors != {}:
            for msg in form.errors.values():
                flash(msg.pop(), category='danger')

            return render_template('register.html', form=form, ulogovan=False)
    else :
        return render_template('register.html', form=form, ulogovan=False)


@user.route("/login", methods=["GET","POST"])

def login():
    form=LoginForm()
    if request.method=="POST":
        if form.validate_on_submit():
            logovanje=LoginSchema().load({"email":form.email.data,"password":form.password.data})
            data = jsonify(logovanje).get_data()
            zahtev = req.Request(f"{adresa}/login")
            zahtev.add_header('Content-Type', 'application/json; charset=utf-8')
            zahtev.add_header('Content-Length', len(data))
            try:
                ret = req.urlopen(zahtev, data)
            except HTTPError as e:
                 flash(e.read().decode(),category='danger')
                 return render_template("login.html",form=form, ulogovan=False)

            user=json.loads(ret.read())
            session["user"]=user
            flash(f"Uspesno ste ulogovani kao {user['ime']}",category='primary')
            return redirect(url_for("index"))
        if form.errors != {}:
            for msg in form.errors.values():
                flash(msg.pop(), category='danger')

            return render_template('login.html', form=form, ulogovan=False)
    else :
        return render_template('login.html', form=form, ulogovan=False)


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
                zahtev = req.Request(f"{adresa}/change_user")
                zahtev.add_header('Content-Type', 'application/json; charset=utf-8')
                zahtev.add_header('Content-Length', len(data))
                try:
                    ret = req.urlopen(zahtev, data)
                except HTTPError as e:
                    flash(e.read().decode(),category='danger')
                    return render_template('change.html', form=form, ulogovan=True)

                user=json.loads(ret.read())
                user['stanja'] = session['user']['stanja'] 
                session["user"]=user
                flash(f"Uspesno ste promenili korisnicke podatke! ",category='primary')
                return redirect(url_for("index"))
            if form.errors != {}:
                for msg in form.errors.values():
                    flash(msg.pop(), category='danger')

                return render_template('change.html', form=form, ulogovan=True)
        if request.method == 'GET':
            user = session['user']
            form.ime.data = user['ime']
            form.prezime.data = user['prezime']
            form.grad.data = user['grad']
            form.adresa.data = user['adresa']
            form.drzava.data = user['drzava']
            form.telefon.data = user['telefon']
            form.email.data = user['email']

            return render_template('change.html', form=form, ulogovan=True)

    else:
        return redirect(url_for('user.login'))

@user.route('/stanja', methods=['GET', 'POST'])
def stanja():
    if 'user' in session:
        form = ZamenaForm()
        coin_data = coin.get_coins_markets(vs_currency="usd")
        if request.method == 'GET':
            izbori = [(cd['symbol'], cd['name']) for cd in coin_data]
            form.valuta_posle.choices = izbori

            return render_template('stanja.html', stanja=session['user']['stanja'], form=form, ulogovan=True)
        else :
            if form.is_submitted():
                cena_pre = None
                cena_posle = None
                for cd in coin_data:
                    if cd['symbol'] == form.valuta_posle.data:
                        cena_posle = cd['current_price']
                    
                    if cd['symbol'] == request.form.get('valuta_pre'):
                        cena_pre = cd['current_price']

                if cena_pre and cena_posle:
                    data = {'email':session['user']['email'], 'kolicina':form.kolicina.data, 'valuta_pre':request.form.get('valuta_pre'),
                        'valuta_posle':form.valuta_posle.data, "cena_pre":cena_pre, 'cena_posle':cena_posle}
                    data = jsonify(data).get_data()
                    zahtev = req.Request(f"{adresa}/zamena")
                    zahtev.add_header('Content-Type', 'application/json; charset=utf-8')
                    zahtev.add_header('Content-Length', len(data))
                    try:
                        ret = req.urlopen(zahtev, data)
                        user = json.loads(ret.read())
                        session['user'] = user
                        return redirect(url_for('user.stanja'))
                    except HTTPError as e:
                        flash(e.read().decode(), category='danger')
                        return redirect(url_for('user.stanja'))
            
            if form.errors != {}:
                for msg in form.errors.values():
                    flash(msg.pop(), category='danger')
                return redirect(url_for('user.stanja'))
    else:
        return redirect(url_for('user.login'))


@user.route('/verifikacija',methods=['GET','POST'])
def verifikacija():
    form = KarticaForm()
    if 'user' in session:
        if not session['user']['verifikovan']:
            if request.method == "POST":
                if form.validate_on_submit():
                    data={"ime":form.ime.data,"brojKartice":form.brojKartice.data,"datumIsteka":form.datumIsteka.data,"kod":form.kod.data,"email":session["user"]['email']} 
                    data = jsonify(data).get_data()
                    zahtev = req.Request(f"{adresa}/verifikacija")
                    zahtev.add_header('Content-Type', 'application/json; charset=utf-8')
                    zahtev.add_header('Content-Length', len(data))
                    try:
                        ret = req.urlopen(zahtev, data)
                        session['user']['verifikovan']=True

                    except HTTPError as e:
                        flash(e.read().decode(),category='danger')
                        return redirect(url_for("user.verifikacija"))

                    flash(ret.read().decode(),category='primary')
                    return redirect(url_for("user.index"))
                if form.errors != {}:
                    for msg in form.errors.values():
                        flash(msg.pop(), category='danger')

                return render_template('kartica.html', form=form, ulogovan=True)
            else :
                    return render_template('kartica.html', form=form, ulogovan=True)
        else:
            flash('Vas nalog je već verifikovan!', category='success')
            return redirect(url_for('user.index'))
    else:
        return redirect(url_for('user.login'))
               
@user.route('/')
def index():
    if 'user' in session:
        return render_template('index.html', ulogovan=True)
    else:
        return render_template('index.html', ulogovan=False)