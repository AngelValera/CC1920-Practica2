### --------------------------------------
### Código para el Servicio 2 - API
### Angel Valera Motos - P2 - CC
### --------------------------------------
import requests
import json
import os
import zipfile
import pickle
from datetime import datetime, timedelta
import time

api_key = os.environ["API_KEY"]

class PrediccionAPI:
    def __init__(self):        
        request = requests.get(
            'https://opendata.aemet.es/opendata/api/prediccion/especifica/municipio/horaria/18087', verify=False, headers={'api_key': api_key})
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
        periodoT = []
        temperatura = []
        humedad = []

        for n in range(tiempo):
            for val in self.data[0]["prediccion"]["dia"][n]["temperatura"]:
                periodoT.append(val["periodoT"])
                temperatura.append(val["value"])
            for val in self.data[0]["prediccion"]["dia"][n]["humedadRelativa"]:
                humedad.append(val["value"]) 
        total = len(periodoT)
        resultado = '{ "origen": '+json.dumps(self.data[0]["origen"])+', "forecast": ['
        for n in range(tiempo):
            fecha = self.data[0]["prediccion"]["dia"][n]["fecha"]
            resultado += '{ "date": "'+fecha+'", "values": ['
            for i in range(total):
                resultado += '{"hour" : "' + \
                    periodoT[i]+':00", "temp": ' + \
                    temperatura[i]+', "hum": '+humedad[i]+'}'
                if i != total-1:
                    resultado += ","
            resultado += ']}'
            if n != tiempo-1:
                resultado += ","
        resultado += ']}'
        return json.loads(resultado), 200
    
