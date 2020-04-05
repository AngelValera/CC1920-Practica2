### --------------------------------------
### Airflow scheduler
### Angel Valera Motos - P2 - CC 
### --------------------------------------
###

# incluimos las bibliotecas necesarias
from datetime import timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.trigger_rule import TriggerRule
from airflow.utils.dates import days_ago
import requests
import os
from sqlalchemy import create_engine
import sqlalchemy.dialects.mysql.pymysql
import pandas 

# Inluir biliotecas PIP

# Definimos los argumentos del DAG 
# -------------------------------------------------------------------------------------------------
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(2),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

#Inicialización del grafo DAG de tareas para el flujo de trabajo
# -------------------------------------------------------------------------------------------------
dag = DAG(
    'Flujo_P2_CC',
    default_args=default_args,
    description='Grafo que establece el flujo de tareas para la práctica 2 de CC',
    schedule_interval=timedelta(days=1),
)
# Funciones auxiliares
# -------------------------------------------------------------------------------------------------
def prepararDirectorio(pathDir):
    if not os.path.isdir(pathDir):
       os.mkdir(pathDir)


def limpiarYCombinarDatos():
    DF_Hum = pandas.read_csv(
        "/tmp/workflow/humidity.csv")[['datetime', 'San Francisco']]
    DF_Temp = pandas.read_csv(
        "/tmp/workflow/temperature.csv")[['datetime', 'San Francisco']]
    # Renombrar las columnas:
    DF_Hum = DF_Hum.rename(
        columns={'datetime': 'DATE', 'San Francisco': 'HUM'})
    DF_Temp = DF_Temp.rename(
        columns={'datetime': 'DATE', 'San Francisco': 'TEMP'})
    # Merge:
    NuevoDF = pandas.merge(DF_Temp, DF_Hum, on='DATE')
    # Borrar los NaN:
    NuevoDF = NuevoDF.dropna()
    # Para aligerar el procesamiento vamos a seleccionar solo 1000 muestras 
    # del conjunto de datos de manera aleatoria
    NuevoDF = NuevoDF.sample(n=1000, random_state=1)
    # Exportamos el nuevo DataFrame a fichero CSV
    NuevoDF.to_csv(r'/tmp/workflow/datos.csv', index=False)


def AlmacenarDatos():
    Datos = pandas.read_csv("/tmp/workflow/datos.csv")
    sqlEngine = create_engine(
        'mysql+pymysql://angelvm:003577@127.0.0.1/SanFrancisco', pool_recycle=3600)
    dbConnection = sqlEngine.connect()
    tableName = 'DatosTemHum'
    try:
        Datos.to_sql(tableName, dbConnection, if_exists='replace')
    except ValueError as vx:
        print(vx)
    except Exception as ex:
        print(ex)
    else:
        print("Table %s created successfully." % tableName)
    finally:
        dbConnection.close()

# -------------------------------------------------------------------------------------------------
# Tarea 1: Preparar entorno
PrepararEntorno = PythonOperator(
    task_id='PrepararEntorno',   
    python_callable=prepararDirectorio,
    op_kwargs={'pathDir': '/tmp/workflow/'},
    dag=dag,
)

# Tarea 2-A: Descargar datos de Humedad
DescargarHumedad = BashOperator(
    task_id='DescargarHumedad',
    depends_on_past=False,    
    bash_command='wget --output-document /tmp/workflow/humidity.csv.zip https://github.com/manuparra/MaterialCC2020/raw/master/humidity.csv.zip',
    
    dag=dag
)

# Tarea 2-B: Descargar datos de Temperatura
DescargarTemperatura = BashOperator(
    task_id='DescargarTemperatura',
    depends_on_past=False,
    bash_command='curl -L -o /tmp/workflow/temperature.csv.zip https://github.com/manuparra/MaterialCC2020/raw/master/temperature.csv.zip',
    dag=dag
)

# Tarea 3-A: Descomprimir datos de humedad 
DescomprimirHumedad = BashOperator(
    task_id='DescomprimirHumedad',
    depends_on_past=False,
    #trigger_rule=TriggerRule.ALL_SUCCESS,
    bash_command='unzip -o /tmp/workflow/humidity.csv.zip -d /tmp/workflow ',
    dag=dag
)

# Tarea 3-B: Descomprimir datos de Temperatura
DescomprimirTemperatura = BashOperator(
    task_id='DescomprimirTemperatura',
    depends_on_past=False,
    #trigger_rule=TriggerRule.ALL_SUCCESS,
    bash_command='unzip -o /tmp/workflow/temperature.csv.zip -d /tmp/workflow ',
    dag=dag
)

# Tarea 4: Eliminamos los ficheros comprimidos una vez que se han descomprimido
LimpiarZIPEntorno = BashOperator(
    task_id='LimpiarZIPEntorno',
    depends_on_past=False,
    trigger_rule=TriggerRule.ALL_SUCCESS,
    bash_command='rm /tmp/workflow/temperature.csv.zip; rm /tmp/workflow/humidity.csv.zip',
    dag=dag
)

# Tarea 5: Combinar ficheros csv
CombinarDatos = PythonOperator(
    task_id='CombinarDatos',
    python_callable=limpiarYCombinarDatos,   
    dag=dag,
)

# Tarea 6: Eliminamos los ficheros antiguos para dejar solamente el que nos interesa
LimpiarCSVEntorno = BashOperator(
    task_id='LimpiarCSVEntorno',
    depends_on_past=False,
    trigger_rule=TriggerRule.ALL_SUCCESS,
    bash_command='rm /tmp/workflow/temperature.csv; rm /tmp/workflow/humidity.csv',
    dag=dag
)

# Tarea 7: Paramos todos los servicios si estaban en ejecución
PararServicios = BashOperator(
    task_id='PararServicios',
    depends_on_past=False,
    bash_command='docker-compose -f ~/airflow/dags/CC1920-Practica2/docker-compose.yml down ',
    dag=dag,
)

# Tarea 8: Iniciamos el servicio de MariaDB
IniciarBD = BashOperator(
    task_id='IniciarDB',
    depends_on_past=False,
    bash_command='docker-compose -f ~/airflow/dags/CC1920-Practica2/docker-compose.yml up -d MariaDB',
    dag=dag,
)

# Tarea 9: Almacenamos los datos en la Base de Datos
AlmacenarDatos = PythonOperator(
    task_id='AlmacenarDatos',
    depends_on_past=False,
    python_callable=AlmacenarDatos,
    dag=dag,
)


# DEPENDENCIAS
# -------------------------------------------------------------------------------------------------
PrepararEntorno.set_downstream([DescargarHumedad, DescargarTemperatura])
DescomprimirHumedad.set_upstream(DescargarHumedad)
DescomprimirTemperatura.set_upstream(DescargarTemperatura)
LimpiarZIPEntorno.set_upstream([DescomprimirHumedad, DescomprimirTemperatura])
CombinarDatos.set_upstream(LimpiarZIPEntorno)
LimpiarCSVEntorno.set_upstream(CombinarDatos)
PararServicios.set_upstream(LimpiarCSVEntorno)
IniciarBD.set_upstream(PararServicios)
AlmacenarDatos.set_upstream(IniciarBD)
