#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request
from flask_migrate import Migrate

from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return '<h1>Bakery GET-POST-PATCH-DELETE API</h1>'

@app.route('/bakeries')
def bakeries():

    bakeries = Bakery.query.all()
    bakeries_serialized = [bakery.to_dict() for bakery in bakeries]

    response = make_response(
        jsonify(bakeries_serialized),
        200
    )
    return response

@app.route('/bakeries/<int:id>', methods=['GET', 'PATCH'])
def bakery_by_id(id):
    # Find the bakery to update using the ID.
    bakery = Bakery.query.filter_by(id=id).first()
    if bakery == None:
        response_body = {
            'message': 'This record does not exist in our database. Please try again.'
        }
        response = make_response(jsonify(response_body), 404)
    else:
        if request.method == 'GET':
            bakery_dict = bakery.to_dict()
            response = make_response(jsonify(bakery_dict), 200)
            return response
        elif request.method == 'PATCH':
            # Access the data in the body of the request.
            for attr in request.form:
                # update the record's attributes using request.form.
                # setattr() allows us to use variable values as attribute names
                # when we don't know which fields are being updated
                setattr(bakery, attr, request.form.get(attr))
            # Use that data to update the bakery in the database. 
            db.session.add(bakery)
            db.session.commit()

            bakery_dict = bakery.to_dict()
            response = make_response(jsonify(bakery_dict), 200)
            # Send a response with updated bakery as JSON.
            return response

@app.route('/baked_goods/by_price')
def baked_goods_by_price():
    baked_goods_by_price = BakedGood.query.order_by(BakedGood.price.desc()).all()
    baked_goods_by_price_serialized = [ 
        bg.to_dict() for bg in baked_goods_by_price
    ]
    
    response = make_response(jsonify(baked_goods_by_price_serialized), 200)
    return response

@app.route('/baked_goods/most_expensive')
def most_expensive_baked_good():
    most_expensive = BakedGood.query.order_by(BakedGood.price.desc()).first()
    most_expensive_serialized = most_expensive.to_dict()

    response = make_response(
        jsonify(most_expensive_serialized),
        200
    )
    return response

@app.route('/baked_goods', methods=['GET', 'POST'])
def baked_goods():
    # from flask import request!!!
    if request.method == 'GET':
        baked_goods = []
        for baked_good in BakedGood.query.all():
            baked_good_dict = baked_good.to_dict()
            baked_goods.append(baked_good_dict)
        response = make_response(jsonify(baked_goods), 200)
        return response
    elif request.method == 'POST':
        # new_bg = BakedGood(
        #     name=request.form.get_json()['name'],
        #     price=request.form.get_json()['price'],
        #     bakery_id=request.form.get_json()['bakery_id'],
        # )
        #Below is Deprecated in the Python version 3.8.13, use above!!!!
        new_bg = BakedGood(
            # Access the data in the body of the request.
            # create a new record using the attributes passed in the request
            name=request.form.get('name'),
            price=request.form.get('price'),
            bakery_id=request.form.get('bakery_id'),
        )
        # Use that data to create a new bg in the database.
        db.session.add(new_bg)
        db.session.commit()
        # It's important that we create bg_dict after committing the review to 
        # the database, as this populates it with an ID and data from its bakery
        bg_dict = new_bg.to_dict()
        # Send a response with newly created bg as JSON
        response = make_response(jsonify(bg_dict), 201)
        return response

# The @app.route decorator accepts methods as a default argument. 
# This is simply a list of accepted methods as strings. 
# By default, this list only contains 'GET'.
@app.route('/baked_goods/<int:id>', methods=['GET', 'DELETE'])
def baked_goods_by_id(id):   
    # Find the bg to delete using the ID.
    bg = BakedGood.query.filter(BakedGood.id == id).first()

    if request.method == 'GET':
        bg_dict = bg.to_dict()
        response = make_response(jsonify(bg_dict), 200)
        return response
    
    elif request.method == 'DELETE':
        # Delete the bg from the database.
        db.session.delete(bg)
        db.session.commit()

        response_body = {
            'delete_successful': True,
            'message': 'BakedGood deleted.'
        }
        # Send a response with the deleted bg as JSON to confirm 
        # that it was deleted successfully, so the frontend can 
        # show the successful deletion to the user
        response = make_response(jsonify(response_body), 200)
        return response
    
if __name__ == '__main__':
    app.run(port=5555, debug=True)
