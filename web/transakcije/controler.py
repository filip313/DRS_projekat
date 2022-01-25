from transakcije import *
from transakcije.forme import UplataForm, PrenosForm,KupovinaForm
from urllib import request as req
from urllib.error import HTTPError
import json


adresa="http://drs-engine.herokuapp.com"

@transakcije.route("/uplata",methods=["GET","POST"])
def uplata():
    form=UplataForm()
    if "user" in session:
        if request.method=='POST':
            if form.validate_on_submit():
                data={"ime":form.ime.data,"brojKartice":form.brojKartice.data,"datumIsteka":form.datumIsteka.data,"kod":form.kod.data,"email":session["user"]['email'],"stanje":form.stanje.data} 
                data = jsonify(data).get_data()
                zahtev = req.Request(f"{adresa}/uplata")
                zahtev.add_header('Content-Type', 'application/json; charset=utf-8')
                zahtev.add_header('Content-Length', len(data))
                try:
                    ret = req.urlopen(zahtev, data)
                    stanja=json.loads(ret.read())
                    session['user']['stanja']=stanja
                    flash(f"Uspesno ste uplatili iznos od {form.stanje.data}!",category='primary')
                    return redirect(url_for("user.stanja"))
                except HTTPError as e:
                    flash(e.read().decode(),category='danger')
                    return render_template("uplata.html",form=form, ulogovan=True)
            
            if form.errors != {}:
                for msg in form.errors.values():
                    flash(msg.pop(), category='danger')

                return render_template('uplata.html', form=form, ulogovan=True)
        else:
            return render_template("uplata.html",form=form, ulogovan=True)
    else:
        return redirect(url_for("user.login"))


@transakcije.route('/prenos', methods=['GET', 'POST'])
def prenos():
    if 'user' in session:
        form = PrenosForm()
        izbori = []
        for s in session['user']['stanja']:
            if s['valuta'] != "USD":
                izbori.append((s['valuta'],s['valuta']))
        form.valuta.choices = izbori
        if request.method == 'POST':
            if form.validate_on_submit():
                data={"posiljalac":session['user']['email'], "primalac":form.primalac.data, "valuta":form.valuta.data, "iznos":form.iznos.data}
                data = jsonify(data).get_data()
                zahtev = req.Request(f"{adresa}/prenos")
                zahtev.add_header('Content-Type', 'application/json; charset=utf-8')
                zahtev.add_header('Content-Length', len(data))
                try:
                    ret = req.urlopen(zahtev, data)
                    flash(ret.read().decode(), category='primary')
                    return redirect(url_for('transakcije.prikaz_transakcija'))
                except HTTPError as e:
                    flash(e.read().decode(), category='danger')
                    return render_template('prenos.html', form=form, ulogovan=True)
            
            if form.errors != {}:
                for msg in form.errors.values():
                    flash(msg.pop(), category='danger')
                return render_template('prenos.html', form=form, ulogovan=True)
        else:
            return render_template('prenos.html', form=form, ulogovan=True)
    else:
        redirect(url_for('user.login'))


@transakcije.route('/prikaz', methods=['GET'])
def prikaz_transakcija():
    if 'user' in session:
        if request.method=='GET':
            try:
                ret = req.urlopen(f'{adresa}/transakcije/{session["user"]["id"]}')
                user = json.loads(ret.read())
                session['user'] = user
                return render_template('transakcije.html', poslate=user['poslate_transakcije'], primljene=user['primljene_transakcije'], ulogovan=True)
            except HTTPError as e:
                flash(e.read().decode(), category='danger')
                return redirect(url_for('index'))
        
    else:
        return redirect(url_for('user.login'))

@transakcije.route('/kupovina',methods=['GET','POST'])
def kupovina():
    if 'user' in session:
        form=KupovinaForm()
        tabela=coin.get_coins_markets(vs_currency="usd")
        if request.method=='GET':
               return render_template('kupovina.html',tabela=tabela,form=form, ulogovan=True)
        else:
            if form.validate_on_submit():
                valuta=request.form.get('symbol')
                cena=request.form.get('cena')
                data={'email':session['user']['email'],'valuta':valuta,'kolicina':form.kolicina.data,'vrednost':cena}
                data = jsonify(data).get_data()
                zahtev = req.Request(f"{adresa}/kupovina")
                zahtev.add_header('Content-Type', 'application/json; charset=utf-8')
                zahtev.add_header('Content-Length', len(data))
                try:
                    ret = req.urlopen(zahtev, data)
                    user=json.loads(ret.read())
                    session['user']=user
                    return redirect(url_for('user.stanja'))
                except HTTPError as e:
                    flash(e.read().decode(), category='danger')
                    return render_template('kupovina.html',tabela=tabela, form=form, ulogovan=True)
            
            if form.errors != {}:
                for msg in form.errors.values():
                    flash(msg.pop(), category='danger')
                return render_template('kupovina.html',tabela=tabela, form=form, ulogovan=True)
    else:
        return redirect(url_for('user.login'))




