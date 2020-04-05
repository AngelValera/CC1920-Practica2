#!/usr/bin/python
# -*- coding: utf-8 -*-
### --------------------------------------
### Código para el testear el Servicio 1 - Arima
### Angel Valera Motos - P2 - CC
### --------------------------------------
import sys
import unittest
import pytest
import app
import prediccion2

prediccion = prediccion2.PrediccionAPI()
app = app.app.test_client()

class Test_Predicciones(unittest.TestCase):

    def test1_ProbocarError(self):
        with pytest.raises(ValueError):
            assert prediccion.ObtenerPrediccion('Prueba')
            
    def test2_ObtenerPredicciones24(self):
        respuesta = app.get('/servicio/v1/prediccion/24horas')
        assert (respuesta.status_code == 200)

    def test3_ObtenerPredicciones48(self):
        respuesta = app.get('/servicio/v1/prediccion/48horas')
        assert (respuesta.status_code == 200)

    def test4_ObtenerPredicciones72(self):
        respuesta = app.get('/servicio/v1/prediccion/72horas')
        assert (respuesta.status_code == 200) 

if __name__ == '__main__':
    pytest.main()
