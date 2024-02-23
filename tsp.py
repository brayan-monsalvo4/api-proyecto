import coordenadas
import requests
import json

# estructura que debe llevar la peticion POST para la api routific
#{
#  "visits": {
#    "order_1": {
#      "location": {
#        "name": "6800 Cambie",
#        "lat": 49.227107,
#        "lng": -123.1163085
#      }
#    },
#    "order_2": {
#      "location": {
#        "name": "3780 Arbutus",
#        "lat": 49.2474624,
#        "lng": -123.1532338
#      }
#    },
#    "order_3": {
#      "location": {
#        "name": "800 Robson",
#        "lat": 49.2819229,
#       "lng": -123.1211844
#      }
#    }
#  },
#  "fleet": {
#    "vehicle_1": {
#      "start_location": {
#        "id": "depot",
#        "name": "800 Kingsway",
#        "lat": 49.2553636,
#        "lng": -123.0873365
#      },
#      "end_location": {
#        "id": "depot",
#        "name": "800 Kingsway",
#        "lat": 49.2553636,
#        "lng": -123.0873365
#      }
#    }
#  }
#}

#la funcion get_route() estructura la peticion POST para la api
#la api retorna la mejor ruta para una serie de destinos
#a partir de una direccion inicial
#parte de una direccion inicial, recorre todas las direcciones y retorna al punto inicial (ciclo)
def get_route(direccion_inicial, lista_direcciones) -> dict :

    url = "https://api.routific.com/v1/vrp"
    key = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI2MzcxN2I2YmNjODg3NzAwMTgyOGJiMGYiLCJpYXQiOjE2NjgzODE1NDd9.xwwGIX9DEDAKZee24BZ7hN_FDBERLpiXZjFV2F4rl34"

    data = dict()
    #dentro de visitas se guardaran todas las direcciones destino
    visitas = dict()

    #dentro de fleet se guardaran los lugares de donde partira (base) y donde regresara (base)
    fleet = dict()
    i = 1

    for lugar in lista_direcciones:
        #obtiene las coordenadas del primer destino (requerido por la api de routific)
        #guarda la latitud y longitud
        ubicacion = coordenadas.get_coordinates(lugar)
        l1 = ubicacion["lat"]
        l2 = ubicacion["lng"]

        #en un diccionario  location guarda la direccion, latitud y longitud de dicho destino
        location = {"name":lugar, "lat": l1, "lng":l2}

        #en el diccionario visitar agrega un nuevo diccionario, con la clave "order_{i}" y como
        #valor tiene al diccionario location
        visitas.update({f'order_{i}' : {"location":location}})
        i+=1

        #se limpia el diccinario auxiliar
        ubicacion.clear()

    #se limpia el diccionario auxiliar
    ubicacion.clear()

    #se obtiene nuevamente las coordenadas de la base
    ubicacion = coordenadas.get_coordinates(direccion_inicial)
    lt = ubicacion["lat"]
    lg = ubicacion["lng"]

    #se guarda en localizacion un diccionario con la direccion de la base
    localizacion = {"name":direccion_inicial, "lat":lt, "lng":lg}

    #dentro de fleet guadara la direccion donde partira (base) y donde regresara (base tambien)
    fleet = {"vehicle_1":{"start_location":localizacion, "end_location":localizacion}}

    #en data se guarda las direcciones destino (visits) y los puntos de inicio y fin (fleet)
    data ={"visits":visitas, "fleet":fleet}


    headers = {"Content-Type": "application/json", "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI2M2Q2YTc4YjQ1ODUxNTAwMTg4YzZkMzgiLCJpYXQiOjE2NzUwMTE5Nzl9.wFVHZ9Z1UWmOm7CXhNZdq4ObGGj9UXqs0K9bssIDP00"}

    #se guarda la respuesta de la request POST de la api
    response = requests.request("POST", url, json=data, headers=headers)

    #print(response.json())


    return response.json()
