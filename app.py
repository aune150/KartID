import json
import os
import sys
from datetime import datetime, timedelta, date
import logging
from EventorAPI import EventorAPI

from flask import Flask, jsonify, render_template, request, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from sqlalchemy import desc, select, distinct
from wtforms import DateField, SelectField, StringField, SubmitField
from wtforms.fields.numeric import FloatField, IntegerField
from wtforms.validators import DataRequired

# Initialize Flask App
app = Flask(__name__)
app.config["SECRET_KEY"] = "Dette er en veldig hemmelig nøkkel"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///kart2.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
EventorAPI = EventorAPI()
logger = logging.getLogger(__name__)
logging.basicConfig(filename='log.log', level=logging.INFO)

# Create model
class base(db.Model):
    nr = db.Column(db.Integer, primary_key=True)
    dato_lagd = db.Column(db.DateTime, default=datetime.now())
    navn = db.Column(db.String(200))
    dato = db.Column(db.Date)
    arr = db.Column(db.String(100))
    typ = db.Column(db.String(10))
    klasse = db.Column(db.String(10))
    kommune = db.Column(db.String(50))
    sted = db.Column(db.String(100))
    hva = db.Column(db.String(20))
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    eventorID = db.Column(db.String(10))

    def __str__(self) -> str:
        return "<navn %r>" % self.navn
    
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class skjema(FlaskForm):
    nr = IntegerField("ID", validators=[DataRequired()])
    navn = StringField("Navn", validators=[DataRequired()])
    dato = DateField("Dato", validators=[DataRequired()])
    arr = StringField("Arrangør")
    klasse = StringField("Klasse")
    kommune = StringField("Kommune")
    sted = StringField("Sted")
    hva = SelectField('Hva', choices=[("Skog", "Skog"), ("Sprint", "Sprint"), ("Annet", "Annet"), ("Mellom", "Mellom"), ("Stafett", "Stafett"), ("Sprint", "Sprint"), ("Lang", "Lang"), ("Ultralang", "Ultralang"), ("Postplukk", "Postplukk"), ("Annet", "Annet")], validators=[DataRequired()])
    typ = SelectField('Type', choices=[("Løp", "Løp"), ("Trening", "Trening")], validators=[DataRequired()])
    eventorID = StringField("EventorID")
    lat = FloatField("Lat")
    lng = FloatField("Lng")
    lagre = SubmitField("Lagre")
    slett = SubmitField("Slett")


@app.errorhandler(404)
def error_404(error):
    return f"404, {error}", 404


@app.route("/")
def hjem():
    kart = base.query.order_by(desc(base.dato)).limit(10).all()
    return render_template("hjem.html", kart=kart)


@app.route("/ny", methods=["GET", "POST"])
def ny():
    navn = None
    form = skjema()
    if form.is_submitted():
        kart = base(typ=form.typ.data, navn=form.navn.data, dato=form.dato.data, arr=form.arr.data, klasse=form.klasse.data, kommune=form.kommune.data, sted=form.sted.data, hva=form.hva.data, lat=form.lat.data, lng=form.lng.data, eventorID=form.eventorID.data)
        db.session.add(kart)
        db.session.commit()
        return viser(kart.nr)
    return render_template("ny.html", navn=navn, form=form)


@app.route("/søk", methods=["GET", "POST"])
def søk(navn=None):
    if request.method == "POST":
        kart = base.query.filter(base.navn.like('%' + request.form["søk"] + '%'))
        return render_template("vis.html", kart=kart)
        

@app.route("/vis")
def vis():
    args = request.args.to_dict()

    kart = base.query
    
    typer = args.get("typ", "Løp,Trening").split(",")
    kart = kart.filter(base.typ.in_(typer))

    startDato = args.get("startDato", (date.today()-timedelta(days=2000)).isoformat())
    sluttDato = args.get("sluttDato", date.today().isoformat())
    kart = kart.filter(startDato <= base.dato).filter(base.dato <= sluttDato)

    arr = args.get("arr", "*").split(",")
    if arr[0] != "*":
        kart = kart.filter(base.arr.in_(arr))
    
    kart = kart.order_by(desc(base.dato))
    
    antall = args.get("antall", "50"); antall = int(antall)
    kart = kart.limit(antall)
    
    return render_template("vis.html", typ=typer, kart=kart)


@app.route("/vis/<int:id>")
def viser(id):
    kart = base.query.get(id)
    if kart is not None:
        return render_template("viser.html", kart=kart)
    else:
        error_404(f"Fant ikke {id} i databasen, legg den til!")


@app.route("/rediger/<int:id>", methods=["GET", "POST"])
def rediger(id):
    kart = base.query.get(id)
    if request.method == "POST":
        if "slett" in request.form:
            base.query.filter_by(nr=id).delete()
            db.session.commit()
            return hjem()
        #kart.nr = request.form["nr"]
        kart.navn = request.form["navn"]
        kart.dato = datetime.fromisoformat(request.form["dato"])
        kart.arr = request.form["arr"]
        kart.klasse = request.form["klasse"]
        kart.kommune = request.form["kommune"]
        kart.sted = request.form["sted"]
        kart.hva = request.form["hva"]
        kart.lat = request.form["lat"]
        kart.lng = request.form["lng"]
        kart.typ = request.form["typ"]
        kart.eventorID = request.form["eventorID"]
        db.session.commit()
        return viser(id)
    if kart is not None:
        form = skjema()
        form.nr.data = kart.nr
        form.navn.data = kart.navn
        form.dato.data = kart.dato
        form.arr.data = kart.arr
        form.klasse.data = kart.klasse
        form.kommune.data = kart.kommune
        form.sted.data = kart.sted
        form.hva.data = kart.hva
        form.lat.data = kart.lat
        form.lng.data = kart.lng
        form.typ.data = kart.typ
        form.eventorID.data = kart.eventorID
        if form.lat.data is None:
            form.lat.data = 63.43
        if form.lng.data is None:
            form.lng.data = 10.39
        return render_template("rediger.html", form=form)
    else:
        print(3)
        return error_404(f"Fant ikke {id} i databasen, legg det til")


@app.route("/kart")
def kartIkart():
    kart = base.query.order_by(desc(base.dato))
    return render_template("kartikart.html", kart=kart)

@app.route("/kobleEventor")
def kobleEventor():
    args = request.args.to_dict()
    startDato = args.get("startDato", (date.today()-timedelta(days=30)).isoformat())
    sluttDato = args.get("sluttDato", date.today().isoformat())
    kunUten = args.get("kunUten", "false")
    mineLop = args.get("mineLop", "true")
    if mineLop == "true":
        E = EventorAPI.mineLop(startDato, sluttDato).events_valg()
    else:
        E = EventorAPI.Lop(startDato, sluttDato).events_valg()
        if type(E) == int:
            flash(f"Feilmelding fra Eventor, kode {E}", category="error")
            return render_template("linkEventor.html", events=[], startDato=startDato, sluttDato=sluttDato, valg={}, kunUten=kunUten, mineLop=mineLop)
    logger.debug(E)
    events = base.query.filter(base.typ=="Løp").filter(base.dato >= startDato).filter(base.dato <= sluttDato)
    if kunUten == "true":
        events = events.filter(base.eventorID == "")
    return render_template("linkEventor.html", events=events, startDato=startDato, sluttDato=sluttDato, valg=E, kunUten=kunUten, mineLop=mineLop)

@app.route("/api/oppdaterEventorID", methods=["POST"])
def apiOppdaterEventorID():
    data = json.loads(request.data)
    nr = data["NR"]
    nyEventorID = data["nyEventorID"]
    startDato = data["startDato"]
    sluttDato = data["sluttDato"]
    kart = base.query.get(nr)
    kart.eventorID = int(nyEventorID)
    db.session.commit()
    #events = base.query.filter(base.typ=="Løp").filter(base.dato >= startDato).filter(base.dato <= sluttDato)
    events = base.query.filter(base.nr == nr)
    return jsonify([{"nr":e.nr, "eventorID":e.eventorID} for e in events])

port = int(os.environ.get('PORT', 8080))

if len(sys.argv) > 1:
    host = sys.argv[1]
else:
    host = "127.0.0.1"
if __name__ == '__main__':
    app.run(threaded=True, port=port, debug=True, host=host)

