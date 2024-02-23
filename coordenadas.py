import requests
import urllib

#funcion para obtener las coordenadas de una direccion, lugar en este caso:

def get_coordinates(lugar) -> dict:
    api_url = "http://www.mapquestapi.com/geocoding/v1/address"
    key = "-"

    url = api_url + urllib.parse.urlencode({"key":key, "location":lugar})
    json_data = requests.get(url).json()
    
    print(url)
    print(json_data["results"][0]["locations"][0]["latLng"])
    
    #retorna la informacion en forma de diccionario, con la sig. estructura:
    #{
    #   "lat" : <valor xd>,
    #   "lng" : <valor xd>    
    #}

    return json_data["results"][0]["locations"][0]["latLng"]
