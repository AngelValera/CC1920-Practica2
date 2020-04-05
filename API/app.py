#!/usr/bin/python
# -*- coding: utf-8 -*-
### --------------------------------------
### API Servicio 1 - Arima
### Angel Valera Motos - P2 - CC
### --------------------------------------

# Framework Flask
from flask import Flask, jsonify, Response
import prediccion1
prediccion = prediccion1.PrediccionArima()

app = Flask(__name__)

#------------------------------------------------------------------------------------------------------------------
@app.route("/")
def index():
    return Response("Versión 1: Predicción de temperatura y humedad utilizando ARIMA.", status=200)
#------------------------------------------------------------------------------------------------------------------
# Ruta para obtener la predicción de la versión 1 del servicio dependiendo de la hora
@app.route('/servicio/v1/prediccion/<num>horas', methods=['GET'])
def ObtenerPrediccionV1(num):	
	resultado = prediccion.ObtenerPrediccion(num)
	if (len(resultado) > 0):		
		return jsonify(resultado), 200
	else:
		return Response("No hay predicciones de humedad ni de temperatura", status=400)	
#------------------------------------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
	app.run(debug=True, port=4000  )
