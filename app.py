# Required Imports
import os
from flask import Flask, request, jsonify, render_template, url_for
from firebase_admin import credentials, firestore, initialize_app, db
import json


def id_i_liste(liste, key, value) -> bool:
    for i in liste:
        i = liste[i]

        #print(i[key], value)
        #print(type(i[key]), type(value))
        if str(i[key]) == str(value):
            return True
    return False

def stor_bokst(s:str):
    return s[0].upper() + s[1:]

# Initialize Flask App
app = Flask(__name__)
# Initialize Firestore DB
cred = credentials.Certificate('key.json')
default_app = initialize_app(cred, {
    "databaseURL":"https://kart-id-default-rtdb.europe-west1.firebasedatabase.app/"
})
dab = firestore.client()
todo_ref = dab.collection('todos')
base = db.reference("/")

@app.route("/")
def hjem():
    """
    Lager en hjemskjerm med de 10 siste kartene for hver kategori
    """
    text, code = read("trening")
    tabel_T = [json.loads(text.get_data(True))[i] for i in json.loads(text.get_data(True))]
    text, code = read("løp")
    tabel_L = [json.loads(text.get_data(True))[i] for i in json.loads(text.get_data(True))]
    return render_template("hjem.html", tabel_L=tabel_L[-10:], tabel_T=tabel_T[-10:])


@app.route("/vis/<typ>")
def viser(typ):
    """
        Side hvor man kan se på alle kartene for trening eller løp
        typ: trening | løp

        Mangler html
    """
    text, code = read(typ)
    tabel = [json.loads(text.get_data(True))[i] for i in json.loads(text.get_data(True))]
    return render_template("viser.html", kategori=typ, tabel=tabel)


@app.route("/vis/<typ>/<int:id>")
def viser_id(typ, id:int):
    """
        Side der man viser et kart, etterhvert med mulighet for redigering
        typ: trening | løp
        id: 1

    """
    data = base.get()[typ]
    id = int(id)

    if id_i_liste(data, "id", id):        # Sjekker om data har minst en value med key
        l = [{i:data[i]} for i in data if data[i]["id"] == id][0]
        l = l[[i for i in l][0]]
        data_u = [i for i in l if i != "id" and i != "lat" and i != "lng"]
        print(data_u)
        if not "lat" in l.keys():
            l["lat"] = 60
        if not "lng" in l.keys():
            l["lng"] = 10
        return render_template("viser_id_m.html", data=l, data_u=data_u, stor_bokst=stor_bokst, lat=l["lat"], lng=l["lng"], typ=typ)
    
    else:
        return jsonify({"success": False}), 400


@app.route('/add/<typ>', methods=['POST'])
def create(typ):
    """
        Lager et nytt kart i kategori <typ>. Data skal sendes med json
        typ: trening | løp
        data:   {'id': 1, 'dato': '2016-04-17', 'navn': 'O-teknisk trening', 'med': 'STOK', 'øktnr': 0.0, 'kartnr': 0.0, 'klasse': 'B', 'type': 'Sk', 'sted': 'Lyngset', 'kommune': 'Ørland'} | 
                {'id': 1, 'dato': '2014-05-21', 'navn': 'Ungdomsløp', 'arrangør': 'Freidig', 'nivå': 'C', 'klasse': 'H11-12', 'distanse': 'M', 'type': 'U', 'sted': 'Ferista', 'kommune': 'TRD'}
    """
    try:
        base.child(typ).push(request.json)
        return jsonify({"success": True}), 200
    except Exception as e:
        print(f"Error: {e}")
        return f"An Error Occured: {e}"


@app.route('/les/<typ>', methods=['GET'])
def read(typ):
    """
        Lager en liste med kart i kategori <typ> som oppfyller kravene
        typ: trening | løp
        spørring: id=1 | arrangør=Freidig
    """
    try:
        args = request.args.to_dict()
        data = base.get()[typ]
        
        if len(args) > 0:
            key = [i for i in args][0]
            value = int(args[key])
            if id_i_liste(data, key, int(value)):        # Sjekker om data har minst en value med key
                    l = [{i:data[i]} for i in data if data[i][key] == value]
                    return jsonify(l), 200
            else:
                return jsonify({"error":f"Nøkkelen {key} har ikke verdi {value} i databasen"}), 400
        
        else:
            return jsonify(base.get()[typ]), 200

            
    except Exception as e:
        return f"An Error Occured: {e}", 404


@app.route('/update/<typ>', methods=['POST', 'PUT'])
def update(typ):
    """
        Oppdaterer kart med id i <typ>
        typ: trening | løp
        id: 1
    """
    #try:
    data = base.get()[typ]
    id = int(request.args.to_dict()["id"])


    if id_i_liste(data, "id", id):        # Sjekker om data har minst en value med key
        l = [{i:data[i]} for i in data if data[i]["id"] == id]
        id_fire = [i for i in l[0]][0]
        base.child(typ).child(id_fire).update(request.json)
        return jsonify({"success": True}), 200

    else:
        return f"id {id} finnes ikke i {typ}", 400

        
    #except Exception as e:
    #    return f"An Error Occured: {e}"


@app.route('/delete/<typ>', methods=['GET', 'DELETE'])
def delete(typ):
    """
        Sletter kart med id i <typ>
        typ: trening | løp
        id: 1

        Funker ikke enda. Foreløbig må man ha Mq0ylM4c1oACmC_nHyA id fra firebase
    """
    data = base.get()[typ]
    id = int(request.args.to_dict()["id"])


    if id_i_liste(data, "id", id):        # Sjekker om data har minst en value med key
        l = [{i:data[i]} for i in data if data[i]["id"] == id]
        id_fire = [i for i in l[0]][0]
        print("DELETE", typ, id_fire)
        #base.child(typ).child(id_fire).delete()
        return jsonify({"success": True}), 200

    else:
        return f"id {id} finnes ikke i {typ}", 400

    """
    try:
        id = request.args.to_dict()["id"]
        base.child(typ).child(id).delete()
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error Occured: {e}"
    """

@app.route("/js", methods = ["POST"])
def js():
    jsdata = request.get_json()
    print(jsdata)
    return "Hello world"



port = int(os.environ.get('PORT', 8080))


if __name__ == '__main__':
    app.run(threaded=True, host='0.0.0.0', port=port, debug=True)

