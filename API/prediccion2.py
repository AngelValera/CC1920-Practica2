### --------------------------------------
### Código para el Servicio 2 - API
### Angel Valera Motos - P2 - CC
### --------------------------------------
import requests
import json
import os


# URL para solicitar el tiempo en Granada
url = 'https://opendata.aemet.es/opendata/api/prediccion/especifica/municipio/horaria/18087'
headers = {'cache-control': "no-cache"}
querystring = {"api_key":  os.environ["API_KEY"]}


class PrediccionAPI:
    def __init__(self):        
        request = response = requests.request(
            "GET", url, headers=headers, params=querystring, verify=False)
        requestJSON = request.json()        
        dataRequest = requests.get(requestJSON["datos"], verify=False)
        self.Datos = dataRequest.json()
        
    #-------------------------------------------------------------------------------------
    def ObtenerPrediccion(self, periodo):
        # comprobamos que el periodo sea un valor numérico entero
        try:
            tiempo = int(periodo)
        except ValueError:
            raise ValueError("El periodo debe ser un valor entero")    
        tiempo = int(tiempo/24)      

        print(len(self.Datos[0]["prediccion"]["dia"]))

        if (tiempo > len(self.Datos[0]["prediccion"]["dia"])):
            tiempo = len(self.Datos[0]["prediccion"]["dia"])
        periodoT = []
        temperatura = []
        humedad = []

        for t in range(tiempo):
            for val in self.Datos[0]["prediccion"]["dia"][t]["temperatura"]:
                periodoT.append(val["periodo"])
                temperatura.append(val["value"])
            for val in self.Datos[0]["prediccion"]["dia"][t]["humedadRelativa"]:
                humedad.append(val["value"]) 
        
        total = len(periodoT)
        resultado = '{ "origen": ' + \
            json.dumps(self.Datos[0]["origen"])+', '
        
        for t in range(tiempo):
            fecha = self.Datos[0]["prediccion"]["dia"][t]["fecha"]
            resultado += '"date": "'+fecha+'", "values": ['            
            for i in range(total):
                resultado += '{"hour" : "' + \
                    periodoT[i]+':00", "temp": ' + \
                    temperatura[i]+', "hum": '+humedad[i]+'}'
                if i != total-1:
                    resultado += ","            
            resultado += ']'
            if t != tiempo-1:
                resultado += ","
        resultado += '}'
        
        return json.loads(resultado)
    
