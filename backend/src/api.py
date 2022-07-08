import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc, true
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# ROUTES
@app.route('/drinks', methods = ['GET'])
def retrieve_drinks():
    try:
        drinks = Drink.query.all()

        return jsonify({
            'success': True,
            'drinks': [drink.short() for drink in drinks]
        }),200
    except:
        abort(404)

@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drink_detail(token):
    try:
        drinks = Drink.query.all()

        return jsonify({
            'success': True,
            'drinks':[drink.long() for drink in drinks]
        }),200
    except:
        abort(404)

@app.route('/drinks', methods = ['POST'])
@requires_auth('post:drinks')
def add_drink(token):
    body = request.get_json()

    if not ('title' in body and 'recipe' in body):
        abort(422)

    title = body.get('title')
    recipe = body.get('recipe')

    try:
        drink = Drink(title=title, recipe=json.dumps(recipe))
        drink.insert()

        return jsonify({
            'success':True,
            'drinks':[drink.long()]
        }),200
    
    except:
        abort(422)

@app.route('/drinks/<id>', methods = ['PATCH'])
@requires_auth('patch:drinks')
def update_drink(token,id):

    drink = Drink.query.get(id)

    if drink:
        try:
            body = request.get_json()

            title = body.get('title')
            recipe = body.get('recipe')

            if title:
                drink.title = title
            if recipe:
                drink.recipe = json.dumps(recipe)

            drink.update()

            return jsonify({
                'success': True,
                'drinks': [drink.long()]
            }),200
        except:
            abort(422)
    else:
        abort(404)
            

@app.route('/drinks/<id>', methods = ['DELETE'])
@requires_auth('delete:drinks')
def delete_drink_with_id(token,id):

    drink = Drink.query.get(id)
    if drink:
        try:
            drink.delete()
            return jsonify({
                'success':True,
                'delete':id
            }),200
        except:
            abort(422)
    else:
        abort(404)



# Error Handling


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }),422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success':False,
        'error':404,
        'message':'resource not found'
    }),404

@app.errorhandler(AuthError)
def handle_auth_error(ex):
    return jsonify({
        'success':False,
        'error':ex.status_code,
        'message':ex.error
    }),401