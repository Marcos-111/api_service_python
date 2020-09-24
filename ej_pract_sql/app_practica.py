#!/usr/bin/env python

import traceback
import io
import sys
import os
import base64
import json
import requests
import sqlite3

from flask import Flask, request, jsonify, render_template, Response, redirect
import matplotlib
matplotlib.use('Agg')   # Para multi-thread, non-interactive backend (avoid run in main loop)
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.image as mpimg


from config import config

app = Flask(__name__)

script_path = os.path.dirname(os.path.realpath(__file__))

config_path_name = os.path.join(script_path, 'config.ini')

server = config('server', config_path_name)



def clear():
    
    conn = sqlite3.connect('personas.db')

    c = conn.cursor()

    c.execute("""
                DROP TABLE IF EXISTS persona;
            """)

    
    c.execute("""
            CREATE TABLE persona(
                [userId] INTEGER,
                [id] INTEGER PRIMARY KEY AUTOINCREMENT,
                [title] TEXT,
                [completed] BOOL
            );
            """)

    
    conn.commit()

    
    conn.close()



def fill():

    response = requests.get("https://jsonplaceholder.typicode.com/todos")
    data = response.json()
    for row in data:
        insert_persona(row)
    return Response(status=200)

    

def insert_persona(row):
    conn = sqlite3.connect('personas.db')
    c = conn.cursor()
    
    
    x = (row.get('userId'))
    y = (row.get('title')) 
    z = (row.get('completed'))
    values = [x, y, z]    

    
    c.execute("""
        INSERT INTO persona (userId, title, completed)
        VALUES (?,?,?);""", values)

    conn.commit()
    
    conn.close()


def insert_grupo(group):
    
    conn = sqlite3.connect('personas.db')
    
    c = conn.cursor()
    
    c.executemany("""
        INSERT INTO persona (userId, id, title, completed)
        VALUES (?,?,?,?);""", group)

    conn.commit()
    
    conn.close()


def title_completed_count(userId):
    
    conn = sqlite3.connect('personas.db')
    c = conn.cursor()

       
    c.execute('SELECT p.userId FROM persona AS p WHERE p.completed =? AND p.userId =?', [True, userId])
    data = c.fetchall()
    
    titles = 0
    cantidad_titulos = {}
    
    for x in data:
        titles += 1
        
    cantidad_titulos[userId] = titles
    
    conn.commit()
    
    conn.close()
    
    return cantidad_titulos



def html_table(data_table):

    result = '<table border="1">'
    result += '<thead cellpadding="1.0" cellspacing="1.0">'
    result += '<tr>'
    result += '<th>userId</th>'
    result += '<th>Titles</th>'
    result += '</tr>'

    for x in data_table:
       
        result += '<tr>'
        result += '<td>' + str(x[0]) + '</td>'
        result += '<td>' + str(x[1]) + '</td>'
        result += '</tr>'

    
    result += '</thead cellpadding="0" cellspacing="0" >'
    result += '</table>'

    return result



@app.route("/")
def index():

    try:
        result = "<h1>Bienvenido!!</h1>"
        result += "<h2>Endpoints disponibles:</h2>"
        result += "<h3>[GET] /user/{userId}/titles --> cuantos titulos completó el usuario cuyo id es el pasado como parámetro</h3>"
        result += "<h3>[GET] /user/graph --> reporte y comparativa de cuantos títulos completó cada usuario en un gráfico</h3>"
        result += "<h3>[GET] /user/table --> cuantos títulos completó cada usuario en tabla</h3>"
       
        return result
    
    except:
        return jsonify({'trace': traceback.format_exc()})


@app.route("/user/table")
def user_tabla():
    
    try:

        conn = sqlite3.connect('personas.db')
        c = conn.cursor()

        c.execute('SELECT p.userId FROM persona AS p WHERE p.completed =?', (True,))
       
        data = c.fetchall()

        dicc = {}
        
        
        for x in data:
            s = data.count(x)
            dicc[x] = s

        data_table = dicc.items()         
        return html_table(data_table)
    
    except:
        return jsonify({'trace': traceback.format_exc()})

@app.route("/user/<userId>/titles")
def user_titles(userId):
    
    try:

        result = title_completed_count(userId)
        return(result)
    
    except:
        return jsonify({'trace': traceback.format_exc()})
    

@app.route("/user/graph")
def grafico():
    
    u1 = 0
    u2 = 0
    u3 = 0
    u4 = 0
    u5 = 0
    u6 = 0
    u7 = 0
    u8 = 0
    u9 = 0
    u10 = 0
    
    try:

        conn = sqlite3.connect('personas.db')
        c = conn.cursor()

        c.execute('SELECT p.userId FROM persona AS p WHERE completed =?', [True])
        data = c.fetchall()
        
    
        for user in data:
            if user == (1,):
                u1 += 1
            elif user == (2,):
                u2 += 1
            elif user == (3,):
                u3 += 1
            elif user == (4,):
                u4 += 1
            elif user == (5,):
                u5 += 1
            elif user == (6,):
                u6 += 1
            elif user == (7,):
                u7 += 1
            elif user == (8,):
                u8 += 1
            elif user == (9,):
                u9 += 1
            elif user == (10,):
                u10 += 1

        users_titles = [u1, u2, u3, u4, u5, u6, u7, u8, u9, u10]
        users = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        
        
        fig = plt.figure()
        fig.suptitle('Practica', fontsize=16)
        ax1 = fig.add_subplot()
 
        ax1.bar(users, users_titles, label = 'Cantidad titulos por usuario')
        ax1.set_facecolor('whitesmoke')
        ax1.legend()
        
        
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        plt.close(fig)  # Cerramos la imagen para que no consuma memoria del sistema
        return Response(output.getvalue(), mimetype='image/png')
    
    except:
        return jsonify({'trace': traceback.format_exc()})



if __name__ == '__main__':
    
    clear()
    fill()

   

    app.run(host=server['host'],
            port=server['port'],
            debug=True)



