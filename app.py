import json
import os
import sys
from datetime import datetime

from flask import Flask, jsonify, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy, model
from flask_wtf import FlaskForm
from sqlalchemy import desc
from wtforms import DateField, SelectField, StringField, SubmitField
from wtforms.fields.numeric import FloatField, IntegerField
from wtforms.validators import DataRequired

# Initialize Flask App
app = Flask(__name__)
app.config["SECRET_KEY"] = open("key.txt", "r").read()
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///kart.db"
db = SQLAlchemy(app)

# Create model
class base(db.Model):
    nr = db.Column(db.Integer, primary_key=True)
    dato_lagd = db.Column(db.DateTime, default=datetime.utcnow)
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

    def __repr__(self) -> str:
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
    hva = StringField("Hva")
    typ = SelectField('Type', choices=[("Løp", "Løp"), ("Trening", "Trening")], validators=[DataRequired()])
    lat = FloatField("Lat")
    lng = FloatField("Lng")
    lagre = SubmitField("Lagre")
    slett = SubmitField("Slett")


@app.errorhandler(404)
def error_404(error):
    return f"404, {error}", 404


@app.route("/")
def hjem():
    return render_template("hjem.html")


@app.route("/ny", methods=["GET", "POST"])
def ny():
    navn = None
    form = skjema()
    if form.is_submitted():
        kart = base(typ=form.typ.data, navn=form.navn.data, dato=form.dato.data, arr=form.arr.data, klasse=form.klasse.data, kommune=form.kommune.data, sted=form.sted.data, hva=form.hva.data, lat=form.lat.data, lng=form.lng.data)
        db.session.add(kart)
        db.session.commit()
        return viser(kart.nr)
    return render_template("ny.html", navn=navn, form=form)


@app.route("/søk", methods=["GET", "POST"])
def søk(navn=None):
    print(request.method)
    if request.method == "POST":
        #kart = base.query.filter_by(navn=request.form["søk"])
        kart = base.query.filter(base.navn.like('%' + request.form["søk"] + '%'))
        print(kart.order_by(base.navn).all())
        return render_template("vis.html", kart=kart)
        

@app.route("/vis")
def vis():
    kart = base.query.order_by(desc(base.dato))
    """ut = []
    for k in kart:
        k = base.as_dict(k)
        k["dato"] = k["dato"].isoformat()
        k["dato_lagd"] = k["dato_lagd"].isoformat()
        ut.append(k)
    json.dump(ut, open("test.json", "w", encoding="UTF-8"))"""
    return render_template("vis.html", typ="treninger", kart=kart)


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


port = int(os.environ.get('PORT', 8080))

if len(sys.argv) > 1:
    host = sys.argv[1]
else:
    host = "127.0.0.1"
if __name__ == '__main__':
    app.run(threaded=True, port=port, debug=True, host=host)

