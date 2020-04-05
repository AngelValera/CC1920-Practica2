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
headers = {'api_key': api_key}

class PrediccionAPI:
    def __init__(self):        
        request = requests.get(
            'https://opendata.aemet.es/opendata/api/prediccion/especifica/municipio/horaria/18087', verify=False, headers=headers)
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
        s = '{ "origen": '+json.dumps(self.data[0]["origen"])+', "forecast": ['
        for n in range(tiempo):
            fecha = self.data[0]["prediccion"]["dia"][n]["fecha"]
            s += '{ "date": "'+fecha+'", "values": ['
            for i in range(total):
                s += '{"hour" : "' + \
                    periodoT[i]+':00", "temp": ' + \
                    temperatura[i]+', "hum": '+humedad[i]+'}'
                if i != total-1:
                    s += ","
            s += ']}'
            if n != tiempo-1:
                s += ","
        s += ']}'
        return json.loads(s),200       
    
