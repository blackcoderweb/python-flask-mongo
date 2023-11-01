from flask import Flask, request, jsonify, Response
#Driver para trabajar con MongoDB
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
#Serialize MongoDB documents that contain special BSON types, such as  ObjectId
from bson import json_util, ObjectId


app = Flask(__name__)

#Crear cadena de conexión
app.config['MONGO_URI']='mongodb://localhost/pymongo-flask'
#Aquí guardo mi conexión
mongo = PyMongo(app)

#creando rutas
@app.route('/user', methods=['POST'])
def create_user():
    
    username = request.json['username']
    password = request.json['password']
    email = request.json['email']
    
    if username and email and password:
        hashed_password = generate_password_hash(password)
        id = mongo.db.users.insert_one({
            'username': username,
            'password': hashed_password,
            'email': email     
        }).inserted_id
        response = {
            'id': str(id),
            'username': username,
            'password': hashed_password,
            'email': email
        }
        return response
    else:
        return not_found()

@app.route("/users", methods=['GET'])
def get_users():
    users = mongo.db.users.find()
    #Convierto BSON a JSON
    response = json_util.dumps(users)
    return response

@app.route('/user/<id>', methods=['GET'])
def get_user(id):
    user = mongo.db.users.find_one({'_id': ObjectId(id)})
    #Convierto BSON a JSON
    response = json_util.dumps(user)
    return response

@app.route('/user/<id>', methods=['DELETE'])
def delete_user(id):
    mongo.db.users.delete_one({'_id': ObjectId(id)})
    response = jsonify({
        'message': 'User ' + id + ' deleted',
    })
    return response

@app.route('/user/<id>', methods=['PUT'])
def update_user(id):
    # Paso los datos que quiero actualizar
    username = request.json['username']
    password = request.json['password']
    email = request.json['email']
    
    if username and email and password:
        hashed_password = generate_password_hash(password)
        mongo.db.users.update_one({'_id': ObjectId(id)}, {'$set': {
            'username': username,
            'password': hashed_password,
            'email': email
        }})
        response = jsonify({
            'message': 'User ' + id + ' updated',
        })
        return response

@app.errorhandler(404)
def not_found(error=None):
    response = jsonify(
        {
        'message': 'Resource Not Found: ' + request.url,
        'status': 404
    }
    )
    response.status_code = 404
    #mimetype='application/json' es una cabecera que especifica el tipo de dato que se devuelve en la petición
    return Response(response, mimetype='application/json')

#Para que cada vez que hagamos un cambio se reinicie el server
if __name__ == "__main__":
    app.run(debug=True)
    
