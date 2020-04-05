#!/usr/bin/python
# -*- coding: utf-8 -*-
### --------------------------------------
### Código para el testear el Servicio 1 - Arima
### Angel Valera Motos - P2 - CC
### --------------------------------------
import app
import pytest
import tempfile
import os
import sys
sys.path.append('../')


@pytest.fixture
def client():
    app.app.config['TESTING'] = True
    client = app.app.test_client()

    yield client


def test_status(client):
    rv = client.get('/servicio/v1/prediccion/24horas')
    json_data = rv.get_json()
    assert len(json_data) == 24 and rv.status_code == 200


def test_status(client):
    rv = client.get('/servicio/v1/prediccion/48horas')
    json_data = rv.get_json()
    assert len(json_data) == 48 and rv.status_code == 200


def test_status(client):
    rv = client.get('/servicio/v1/prediccion/72horas')
    json_data = rv.get_json()
    assert len(json_data) == 72 and rv.status_code == 200
