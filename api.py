from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
import urllib
import requests
import sqlite3
import tsp
import instrucciones


app = Flask(__name__)
CORS(app)

#sirve para obtener la lista de direcciones que se establecieron como 
#direcciones iniciales, como lo son de algun almacen o sede

#en este endpoint se puede:
# 1. consultar las bases guardadas (GET)
# 2. guardar una base (POST)
# 3. actualizar una base (PUT)
@app.route("/base", methods=["GET","POST","PUT"])
def ubicar_base():

    #se conecta a la base de datos amogus.db

    con = sqlite3.connect("amogus.db")
    cursor = con.cursor()

    
    # Si el metodo es GET, se consulta la base de datos y retorna las direcciones 
    # como un JSON con la siguiente estructura:
    #   {
    #       "resultado" : [
    #                       {
    #                           "direccion" : "<direccion de la base>",
    #                           "numero" : <numero de la base>                                
    #                       }
    #                    ]
    #   }
    #

    if request.method == "GET":

        #se consultan todas las filas de la tabla base en la base de datos amogus.db
        #y se guarda en direccion las filas de la tabla.
        #Cada fila se representa como una lista de tuplas:
        #ej:   [(1, "direccion1"), (2, "direccion 2")]
        direccion = cursor.execute("select rowid,direccion from base").fetchall()            
        con.close()

        #se crea un diccionario que tiene una unica clave, "resultado" y como valor tiene una lista
        #en donde se iran agregando diccionarios con la informaccion de las bases:
        #numero de base y direccion
        respuesta = {"resultado": []}

        #para cada tupla en direccion
        for lista in direccion:
            #se guarda el numero y direccion
            numero = lista[0]
            direccion = lista[1]

            #dentro de la lista de resultado, se agrega un nuevo diccionario con:
            # -el numero de la base dentro de la tabla (rowid)
            # -la direccion
            respuesta.get("resultado").append({"numero" : numero, "direccion" : direccion})

        return respuesta

    #si el metodo es POST, se anade una nueva direccion a la base de datos, el request debe tener la sig. estructura
    #   {
    #       "direccion" : "<direccion>"
    #   }
    
    elif request.method == "POST":        
        #en request_data se guarda el JSON que se mando por el metodo POST
        #se guarda en valores la direccion a agregar a la base de datos
        request_data = request.get_json()
        valores = request_data["direccion"]   

        # "si el numero de filas de la tabla base en donde la direccion es igual a {valores} es diferente de cero..."
        #si la direccion ya se encuentra en la base de datos...
        if (len( cursor.execute("select * from base where direccion=?", (valores,)).fetchall() ) != 0):
            con.close()
            #return {"respuesta": "la direccion ya se registro"}
            return make_response(jsonify({"error": "la direccion ya existe"}), 409)

        #se ejecuta una consulta para insertar la direccion de la base dentro de la tabla
        cursor.execute("insert into base(direccion) values(?)", (valores,))
        con.commit()        
        con.close
        #return {"respuesta" : "ok", "direccion ingresada": valores}
        return make_response(jsonify({"respuesta": "se guardo la direccion correctamente."}), 201)

    #si el metodo es put, se modifica una direccion guardada en la base de datos
    #la request debe llevar el siguiente formato JSON:
    #   {
    #       "numero_base" : <numero-de-la-base-a-actualizar>,
    #       "direccion" : "<nueva direccion>"
    #   }

    elif request.method == "PUT":
        #se guardan los datos de se mandaron a la request
        numero = request.get_json()["numero_base"]
        direccion = request.get_json()["direccion"]

        # si la direccion esta vacia, o el numero es menor a 1, o el numero de registros
        # que tienen como rowid=numero es igual a cero (no existe registro con dicho rowid)...
        if (len(direccion) == 0 or numero < 1 or len( cursor.execute("select * from base where rowid=?", (numero,)).fetchall() ) == 0):
            con.close()
            return make_response(jsonify({"error" : "direccion no encontrada"}), 404)
            #return {"respuesta": "error"}


        cursor.execute("update base set direccion = ? where rowid = ?;", (direccion, numero,))
        con.commit()
        con.close()
        #return {"respuesta":"ok", "direccion actializada" : direccion}
        return make_response(jsonify({"respuesta" : "base actualizada correctamente"}), 200)

#sirve para eliminar una base de la base de datos
#la estructura de la request en formato JSON es:
#   {
#       "numero_base" : <numero-base-a-eliminar>
#   }

@app.route("/eliminar-base", methods=["DELETE"])
def eliminar_base():
    numero = request.get_json().get("numero_base")
    print(numero)
    con = sqlite3.connect("amogus.db")
    cursor = con.cursor()

    if (len( cursor.execute("select * from base where rowid=?", (numero,)).fetchall() ) == 0 or numero == 0):
            con.close()
            #return {"respuesta": "el numero de base no existe"}
            return make_response(jsonify({"error" : "la base no existe"}), 404)

    sql = "delete from base where rowid=?"
    cursor.execute(sql, (numero,))
    con.commit()
    con.close()
    #return {"respuesta":"ok", "base eliminada" : numero}
    return make_response(jsonify({"respuesta" : "base eliminada correctamente"}), 200)


#sirve para obtener la ruta a seguir. La request debe tener la siguiente estructura:
#   {
#       "numero_ruta" : <numero de la base> //corresponde al rowid de las direcciones de las bases, sedes, bodegas, etc
#       "lista_destinos" : ["<direccion del punto de entrega 1>", 
#                              "<direccion del punto de entrefa 2>", ...
#                             ]        
#   }

@app.route("/ruta", methods=["POST"])
def cargar_ruta():
    
    #se guarda el numero de base y la lista de destinos a visitar
    request_data = request.get_json()
    numero_ruta = request_data["numero_ruta"]
    lista_destinos = request_data["lista_destinos"]

    con = sqlite3.connect("amogus.db")
    cursor = con.cursor()
    
    #con el numero de base, se consulta en la base de datos la direccion
    respuesta = cursor.execute("select direccion from base where rowid = ?", (numero_ruta,)).fetchall()

    #si la respuesta es igual a 0 (no hay direcciones que tienen como numero de base {numero_ruta})
    if len(respuesta) == 0:
        con.close()
        return make_response(jsonify({"error": "no se encuentra dicha base"}), 404)

    direccion_base = respuesta[0][0]

    con.close()

    #se llama la funcion get_route() del objeto tsp para calcular la ruta
    #de la respuesta, se guarda la informacion que contiene el diccionario "solutions"
    #detro de dicho diccionario se encuentra el diccionario "vehicle"
    #el cual contiene ordenadamente las direcciones a visitar, partiendo desde la base
    #recorriendo todas las direcciones iniciales para finalmente retornar a la base
    lista = tsp.get_route(direccion_base, lista_destinos)["solution"]["vehicle_1"]

    #se le pasa la respuesta al modulo instrucciones, el cual estructurara la respuesta
    #colocando en orden las direcciones a visitar mas las indicaciones para llegar (en ingles solamente)
    return instrucciones.get_instrucciones(lista)

#@app.route("/login", methods=["GET"])
#def validar_usuario():
#    usuario = request.args.get("user")
#    contrasena = request.args.get("password")
#
#    conn = sqlite3.connect("usuarios.db")
#   cursor = conn.cursor()
#    resultado = cursor.execute("select rowid from usuarios where nombre_usuario=? and contrasena=?", (usuario, contrasena,)).fetchall()
#
#    if (len(resultado) == 0):
#        conn.close()
#        return {"resultado" : "false"}
#    else:
#        conn.close()
#        return {"resultado" : "true"}




if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000)
