from flask import Flask, jsonify, request
import urllib
import requests
import sqlite3

app = Flask(__name__)
api_url = "http://www.mapquestapi.com/directions/v2/route?"
key = "tTnnNUClaD6ZbGzEfMNAAQVPCZsRKfK7"

@app.route('/ruta')
def return_ruta():
    base_address = open("base.txt", "r")
    if(len(res:= base_address.read()) == 0):
        base_address.close()
        return "no se encuentra la direccion de la base, favor de colocar una con /base?base_address=<direccion>"

    base_address.close()
    base_address = open("base.txt", "r") 
    desde = base_address.read()
    hacia = request.args.get("to")
    tipo = request.args.get("routeType")
    url = api_url + urllib.parse.urlencode({"key":key, "from":desde, "to":hacia, "routeType":tipo})
    json_data = requests.get(url).json()
    base_address.close()
    return json_data

@app.route('/base', methods=['GET','POST'])
def set_base():
    con = sqlite3.connect("amogus.db")
    cursor = con.cursor()
    base_address = request.args.get('base_address') 
    tuplita = (base_address,)
    cursor.execute("insert into base(direccion) values(?)", tuplita)
    con.commit()
    con.close()
    return {"base":base_address}


if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000)
