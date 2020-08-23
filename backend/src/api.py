import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

from urllib.request import urlopen
from functools import wraps
from jose import jwt


app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()


AUTH0_DOMAIN = 'cralina-test.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'image'




def insert_sample_drink():
    j = json.loads('[{"color": "0x12122", "name":"Ginger", "parts":2}, {"color": "0x12122", "name":"Jaggery", "parts":2}]')
    print("Got j", j)
    drink1 = Drink(title="Herbal tea", recipe='[{"color": "0x12122", "name":"Ginger", "parts":2}, {"color": "0x12122", "name":"Jaggery", "parts":2}]')
    drink1.insert()
    drink2 = Drink(title="Tulsi tea", recipe='[{"color": "0x12122", "name":"Ginger", "parts":2}, {"color": "0x12122", "name":"Jaggery", "parts":2}]')
    drink2.insert()
    
## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks")
def get_drinks():
    # insert_sample_drink()
    drinks = Drink.query.all()
    drink_list_short = [drink.short() for drink in drinks]
    if len(drink_list_short) == 0:
        abort(404)    
    
    # print("Got drink list:", drink_list_short)
    return jsonify({
        'success': True,
        'drinks': drink_list_short
    })


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drink_detail(payload):
    # print("get_drink_detail: Got authenticated payload is:", payload)

    drinks = Drink.query.all()
    drink_list_long = [drink.long() for drink in drinks]
    if len(drink_list_long) == 0:
        abort(404)
    # print("Got drink list:", drink_list_long)
    return jsonify({
        'success': True,
        'drinks': drink_list_long
    })
    # return 'Access Granted'


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(payload):
    # errno = 0
    # print("add_drink: Got authenticated payload:", payload)
    # req_data_dict = json.loads(request.data)
    # for pair in req_data_dict.items():
    #     print(pair)
    body_json = request.get_json()

    try:
        title = body_json.get('title')
        recipe = json.dumps(body_json.get('recipe'))
        # print("add_drink: Got title:{}\n,recipe:{}, recipe type:{}\n".format(title, recipe, type(recipe)))
        drink = Drink(title= title, recipe = recipe)
        drink.insert()
        # print("Drink inserted")
        # print("add_drink: Got drink", drink.long())
    except Exception as e:
        print(e)
        abort(422)  
        

    # print("Got drink", json.dumps(drink.long()))
    drink_list_single = [drink.long()]

    return jsonify({
        'success': True,
        'drinks': drink_list_single
    })

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(id):
    # print("update_drink: Got drink id {}".format(id))
    errno = 0
    # req_data_dict = json.loads(request.data)
    # for pair in req_data_dict.items():
    #     print(pair)
   
    try:
        # drink = Drink.query.get(id)
        drink = Drink.query.filter_by(id=id).one_or_none()

        if drink == None:
            errno = 404
            abort(errno)
        # print("update_drink: Got existing drink in database:", drink)
        # Updating
        body_json = request.get_json()
        drink.title = body_json.get('title', drink.title)
        recipe_new = body_json.get('recipe', None)
        if recipe_new is not None:
            # recipe = json.dumps(body_json.get('recipe'))
            drink.recipe = json.dumps(recipe_new)
        # print("update_drink: Got new drink ", drink)
            
        drink.update()
        # print("update_drink: Drink updated ", drink)

    except Exception as e:
        print(e)
        if errno == 0:
            abort(422)
        else:
            abort(errno)

    drink_list_single = [drink.long()]

    return jsonify({
        "success": True, "drinks": drink_list_single
    })

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(id):
    # print("delete_drink: Got drink id {}".format(id))
    errno = 0
    # req_data_dict = json.loads(request.data)
    # for pair in req_data_dict.items():
    #     print(pair)
   
    try:
        drink = Drink.query.get(id)

        if drink == None:
            errno = 404
            abort(errno)
            
        # print("delete_drink: Got existing drink in database:", drink)

        # Deleting drink
        drink.delete()
        
        # print("delete_drink: Deleted drink with id:", id)
    except Exception as e:
        print(e)    
        if errno == 0:
            abort(422)
        else:
            abort(errno)

    return jsonify({
        "success": True, "delete": id
    })


## Error Handling
'''
Example error handling for unprocessable entity
'''
# @app.errorhandler(422)
# def unprocessable(error):
#     return jsonify({
#                     "success": False, 
#                     "error": 422,
#                     "message": "unprocessable"
#                     }), 422

@app.errorhandler(404)
def not_found(error):
    return jsonify({
      "success": False,
      "error": 404,
      "message":"resource not found"
    }), 404

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
    "success": False,
    "error": 422,
    "message":"unprocessable"
    }), 422

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
    "success": False,
    "error": 400,
    "message":"bad request"
    }), 400

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
    "success": False,
    "error": 405,
    "message":"method not allowed"
    }), 405



'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''

@app.errorhandler(AuthError)
def auth_err_handler(err_obj):
    return jsonify({
    "success": False,
    "error": err_obj.status_code,
    "message":err_obj.error['error']
    }), err_obj.status_code




'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''



