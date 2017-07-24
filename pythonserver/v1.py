#!flask/bin/python
from flask import Flask, jsonify,make_response,abort,request
import datetime
import mysql.connector
#import pyodbc
import json
import collections

app = Flask(__name__)

tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol', 
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web', 
        'done': False
    }
]

@app.route('/todo/api/v1.0/tasks', methods=['GET'])
def get_tasks():
    #return jsonify({'tasks': tasks})
    cnx = mysql.connector.connect(user="root",password="213", database='warehouse')
    cursor = cnx.cursor()
    
    cursor.execute( """
            SELECT id, Date, ProductCode, ProductName, ProductLot, Barcode, Quantity,invoiceid
            FROM outinvoice
            """)
    rows = cursor.fetchall()
    rowarray_list = []
    for row in rows:
        data={
        'id':row[0],
        'Date' : row[1],
        'ProductCode' : row[2],
        'ProductName' : row[3],
        'ProductLot' : row[4],
        'Barcode' : row[5],
        'Quantity' : row[6],
        'invoiceid' : row[7]
        }
        #t = (row[0], row[1], row[2], row[3],row[4], row[5], row[6])
        rowarray_list.append(data) 
        
    j = json.dumps(rowarray_list)
    cursor.close()
    cnx.close()
    return j
    #return  "size"+ str((len(rows)))
    #return "1"

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    return jsonify({'task': task[0]})
    

    
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

    

@app.route('/todo/api/v1.0/tasks', methods=['POST'])
def create_task():
    if not request.json:
        abort(400)        
        #return "mymessis"
    cnx = mysql.connector.connect(user="root",password="213", database='warehouse')
    cursor = cnx.cursor()
    querry= """
            UPDATE outinvoice SET Barcode = %s, Quantity = %s
            WHERE id= %s 
            """
    barcode= request.json.get('barcode', "")
    quantity = request.json.get('quantity', "")
    id = request.json.get('id', "")
    ProductCode = request.json.get('ProductCode', "")
    ProductLot = request.json.get('ProductLot', "")
    
    #cursor.execute(querry,(barcode,quantity,id))
    cursor.execute ("""
        UPDATE warehouse.outinvoice
        SET Barcode=%s, Quantity=%s
        WHERE id=%s
        """, (barcode, quantity, id))
    s= querry + ';'.join((barcode,quantity,id,ProductCode,ProductLot))
    cnx.commit()
    cursor.close()
    cnx.close()
    return 'edit:'+s, 201

    
@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'title' in request.json and type(request.json['title']) != unicode:
        abort(400)
    if 'description' in request.json and type(request.json['description']) is not unicode:
        abort(400)
    if 'done' in request.json and type(request.json['done']) is not bool:
        abort(400)
    task[0]['title'] = request.json.get('title', task[0]['title'])
    task[0]['description'] = request.json.get('description', task[0]['description'])
    task[0]['done'] = request.json.get('done', task[0]['done'])
    return jsonify({'task': task[0]})


@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    tasks.remove(task[0])
    return jsonify({'result': True})


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')