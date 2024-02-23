import urllib
import requests

#estructura de la lista de direcciones:
#[
#	{
#		"location_id": "base",
#		"location_name": "direccion 1"
#	},
#	{
#		"location_id": "order_2",
#		"location_name": "direccion 2"
#	},
#	{
#		"location_id": "order_1",
#		"location_name": "direccion 3
#	},
#	{
#		"location_id": "base",
#		"location_name": "direccion 4"
#	}
#]

#extrae la lista de instrucciones para llegar a cierto destino.
# Regresa un diccionario con una lista, la cual contiene una serie de diccionarios con el nombre del 
#punto inicial, hacia donde se dirige y la lista de instrucciones para llegar alli

def get_instrucciones(lista_direcciones) -> dict:
    respuesta = dict()
    respuesta.update({"rutas" : []})

    api_url = "http://www.mapquestapi.com/directions/v2/route?"
    key = "tTnnNUClaD6ZbGzEfMNAAQVPCZsRKfK7"
    
    for i in range (0, len(lista_direcciones)-1):
        direccion_1 = lista_direcciones[i]["location_name"]
        direccion_2 = lista_direcciones[(i+1)]["location_name"]

        url = api_url + urllib.parse.urlencode({"key":key, "from":direccion_1, "to":direccion_2})
        #json_data = requests.get(url).json()

        #lista maniobras contiene un diccionario
        lista_maniobras = list(requests.get(url).json()["route"]["legs"][0]["maneuvers"])
        #print("lista maniobras")
        #print(lista_maniobras)

        respuesta["rutas"].append({
                                    "desde" : direccion_1, 
                                    "hacia" : direccion_2,
                                    "instrucciones" : []
                                })

        for instruccion in lista_maniobras:
            respuesta["rutas"][-1]["instrucciones"].append(instruccion["narrative"])
        
    return respuesta

    #respuesta:
#   {
#       "rutas" : [
#           {
#               "desde" : <direccion inicial>,
#               "hacia" : <direccion final>,
#               "instrucciones" : [
#                   "paso 1", "paso 2", "paso 3", ...            
#               ] 
#           }
#       ]
#   }