### --------------------------------------
### Código para el Servicio 1 - Arima
### Angel Valera Motos - P2 - CC
### --------------------------------------
from statsmodels.tsa.arima_model import ARIMA
import pandas 
import pmdarima as pm
import sqlalchemy as db
import os
import zipfile
import pickle
from datetime import datetime, timedelta
import time


class PrediccionArima:
    # En esta función realizamos la conexión a la base de datos 
    # y extraemos una muestra de 1000 datos
    def __init__(self):
        sqlEngine = db.create_engine(
            'mysql+pymysql://angelvm:003577@127.0.0.1/SanFrancisco', pool_recycle=3600)
        dbConnection = sqlEngine.connect()    
        metadata = db.MetaData()
        DatosTemHum = db.Table(
            'DatosTemHum', metadata, autoload=True, autoload_with=sqlEngine)
        # Equivalente a "SELECT * FROM DatosTemHum "
        query = db.select([DatosTemHum])
        ResultProxy = dbConnection.execute(query)
        ResultSet = ResultProxy.fetchall()
        ResultSet = ResultSet[:1000]       
        self.dataframe = pandas.DataFrame(data=ResultSet)
        
    #-------------------------------------------------------------------------------------
    # En esta función generamos un modelo para 
    # la predicción de Temperatura y otro para la prediccion de Humedad
    # Una vez generado el modelo lo guardamos en un fichero
    def CrearModelo(self):        
        # Modelo temperatura
        modeloTemp = pm.auto_arima(self.dataframe[2], start_p=1, start_q=1,
                                    test='adf',       # use adftest to find optimal 'd'
                                    max_p=3, max_q=3,  # maximum p and q
                                    m=1,              # frequency of series
                                    d=None,           # let model determine 'd'
                                    seasonal=False,   # No Seasonality
                                    start_P=0,
                                    D=0,
                                    trace=True,
                                    error_action='ignore',
                                    suppress_warnings=True,
                                    stepwise=True)
        pickle.dump(modeloTemp, open("./Models/modeloTemp.p", "wb"))
        zipObj = zipfile.ZipFile(
            './Models/modeloTemp.zip', 'w', zipfile.ZIP_DEFLATED)
        zipObj.write("./Models/modeloTemp.p")
        zipObj.close()
        # Modelo Humedad 
        modeloHum = pm.auto_arima(self.dataframe[3], start_p=1, start_q=1,
                                    test='adf',       # use adftest to find optimal 'd'
                                    max_p=3, max_q=3,  # maximum p and q
                                    m=1,              # frequency of series
                                    d=None,           # let model determine 'd'
                                    seasonal=False,   # No Seasonality
                                    start_P=0,
                                    D=0,
                                    trace=True,
                                    error_action='ignore',
                                    suppress_warnings=True,
                                    stepwise=True)        
        pickle.dump(modeloHum, open("./Models/modeloHum.p", "wb"))
        zipObj = zipfile.ZipFile(
            './Models/modeloHum.zip', 'w', zipfile.ZIP_DEFLATED)
        zipObj.write("./Models/modeloHum.p")
        zipObj.close()
    #-------------------------------------------------------------------------------------
    # En esta función se realiza una prediccion de temperatura y de humedad
    # partiendo de los modelos ya generados o creando unos nuevos
    def ObtenerPrediccion(self, periodo):
        # comprobamos que el periodo sea un valor numérico entero
        try:
            tiempo = int(periodo)
        except ValueError:
            raise ValueError("El periodo debe ser un valor entero")

        # Comprobamos si existe el modelo y si no existe lo creamos
        if (os.path.isfile('./Models/modeloTemp.zip') == False) or (os.path.isfile('./Models/modeloHum.zip') == False):
            try:
                os.remove("./Models/modeloTemp.zip")
            except:
                pass
            try:
                os.remove("./Models/modeloHum.zip")
            except:
                pass
            self.CrearModelo()

        # Extraemos los modelos 
        with zipfile.ZipFile('./Models/modeloTemp.zip', 'r') as zipObj:
           zipObj.extractall("./")
        
        with zipfile.ZipFile('./Models/modeloHum.zip', 'r') as zipObj:
           zipObj.extractall("./")

        # Cargamos los modelos
        modeloTemp = pickle.load(open('./Models/modeloTemp.p', "rb"))
        modeloHum = pickle.load(open('./Models/modeloHum.p', "rb"))

        # Realizamos las predicciones 
        predTemp, confint = modeloTemp.predict(n_periods=tiempo, return_conf_int=True)
        predHum, confint = modeloHum.predict(n_periods=tiempo, return_conf_int=True)

        # Realizamos el procesamiento para obtener el periodo de horas solicitado
        # partiendo de la hora en la que se realiza la peticion
        fechaInicio = datetime.now() + timedelta(hours=3) # UTC + 2 + 1
        periodo_fechas = pandas.date_range(fechaInicio.replace(
            second=0, microsecond=0), periods=tiempo, freq='H')        
        # Montamos la predicción en formato JSON 
        resultado = []
        for tiempo, temperatura, humedad in zip(periodo_fechas, predTemp, predHum):
            print(temperatura)
            auxTiempo = time.mktime(tiempo.timetuple())             
            resultado.append({'hour': datetime.utcfromtimestamp(
                auxTiempo).strftime('%H:%M'), 'temp': temperatura, 'hum': humedad})
        return resultado

    
