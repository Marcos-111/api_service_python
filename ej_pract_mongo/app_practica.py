#!/usr/bin/env python

import traceback
import io
import sys
import os
import base64
import json
import sqlite3

import numpy as np
from flask import Flask, request, jsonify, render_template, Response, redirect

import matplotlib
matplotlib.use('Agg')   
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.image as mpimg

import requests
import json

import tinymongo as tm
import tinydb

from config import config

app = Flask(__name__)

script_path = os.path.dirname(os.path.realpath(__file__))

config_path_name = os.path.join(script_path, 'config.ini')
server = config('server', config_path_name)

db_name = 'practica'

class TinyMongoClient(tm.TinyMongoClient):
    @property
    def _storage(self):
        return tinydb.storages.JSONStorage

def clear():
    conn = TinyMongoClient()
    db = conn[db_name]

    db.persons.remove({})

    conn.close()


def fill():

    response = requests.get("https://jsonplaceholder.typicode.com/todos")
    data = response.json()
    insert_grupo(data)
    return Response(status=200)


def insert_grupo(group):
    conn = TinyMongoClient()
    db = conn[db_name]

    # Insertar varios documentos, una lista de JSON
    db.persons.insert_many(group)

    # Cerrar la conexión con la base de datos
    conn.close()

def title_completed_count(userId, completed):
    # Conectarse a la base de datos
    conn = TinyMongoClient()
    db = conn[db_name]

    users_id = db.persons.find({"userId": int(userId), "completed": completed}).count()

    titles = 0
    cantidad_titulos = {}
    
    for x in users_id:
        titles += 1
        
    cantidad_titulos[userId] = titles
    
    conn.commit()
    
    conn.close()
    
    return cantidad_titulos


   

@app.route("/show")
def show():

    cursor = db.persons.find()
    data = list(cursor)
    json_string = json.dumps(data, indent=4)
    

    return json_string



# Ruta que se ingresa por la ULR 127.0.0.1:5000
@app.route("/")
def index():
    try:
        result = "<h1>Bienvenido!!</h1>"
        result += "<h2>Endpoints disponibles:</h2>"
        result += "<h3>[GET] /user/{id}/titles --> cuantos titulos completó el usuario cuyo id es el pasado como parámetro</h3>"
        result += "<h3>[GET] /user/graph --> reporte y comparativa de cuantos títulos completó cada usuario en un gráfico</h3>"
        result += "<h3>[GET] /user/table --> cuantos títulos completó cada usuario en tabla</h3>"
       
        return(result)
    except:
        return jsonify({'trace': traceback.format_exc()})


@app.route("/user/table")
def user_tabla():
    try:

        cursor = db.persons.find()
        data = list(cursor)
        json_string = json.dumps(data, indent=4)
        
        return html_table(data)
    except:
        return jsonify({'trace': traceback.format_exc()})

# Ruta que se ingresa por la ULR 127.0.0.1:5000/pulsaciones/{nombre}/historico
@app.route("/user/<id>/titles")
def user_titles(id):
    try:

        result = title_completed_count(id, True)
        return(result)
    except:
        return jsonify({'trace': traceback.format_exc()})
    

# Ruta que se ingresa por la ULR 127.0.0.1:5000/registro
@app.route("/user/graph")
def grafico():
    lista = []
    dicc = {}
    try:

        conn = TinyMongoClient()
        db = conn[db_name]
        cursor = db.persons.find()
        for doc in cursor:

            users_id = db.persons.find({"userId": doc["userId"], "completed": True})
            lista.append(users_id)

        for x["userId"] in lista:
            s = lista.count(x)
            dicc[x] = s

        users = dicc.keys()
        titles = dicc.values()

        fig = plt.figure()
        fig.suptitle('Practica', fontsize=16)
        ax1 = fig.add_subplot()
 
        ax1.bar(users, titles, label='carne')
        ax1.set_facecolor('whitesmoke')
        ax1.legend()
        
        
    
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        plt.close(fig)  # Cerramos la imagen para que no consuma memoria del sistema
        return Response(output.getvalue(), mimetype='image/png')
    except:
        return jsonify({'trace': traceback.format_exc()})


def html_table(data):

    result = '<table border="1">'
    result += '<thead cellpadding="1.0" cellspacing="1.0">'
    result += '<tr>'
    result += '<th>Fecha</th>'
    result += '<th>Nombre</th>'
    result += '<th>Último registro</th>'
    result += '<th>Nº de registros</th>'
    result += '</tr>'

    for row in data:
       
        result += '<tr>'
        result += '<td>' + str(row[0]) + '</td>'
        result += '<td>' + str(row[1]) + '</td>'
        result += '<td>' + str(row[2]) + '</td>'
        result += '<td>' + str(row[3]) + '</td>'
        result += '</tr>'

    
    result += '</thead cellpadding="0" cellspacing="0" >'
    result += '</table>'

    return result
    









if __name__ == '__main__':
    
    clear()
    fill()

   

    app.run(host=server['host'],
            port=server['port'],
            debug=True)


