from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy()
db.init_app(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


# with app.app_context():
#     db.create_all()

@app.route("/")
def home():
    return render_template("index.html")
    

## HTTP GET - Read Record
@app.route('/random', methods=['GET'])
def get_random():
    result = db.session.execute(db.select(Cafe))
    cafes = result.scalars().all()
    random_cafe = random.choice(cafes)
    # return jsonify(can_take_calls=random_cafe.can_take_calls, coffee_price=random_cafe.coffee_price,
    #                has_sockets=random_cafe.has_sockets, has_toilet=random_cafe.has_toilet, has_wifi=random_cafe.has_wifi,
    #                id=random_cafe.id, img_url=random_cafe.img_url, location=random_cafe.location, map_url=random_cafe.map_url,
    #                name=random_cafe.name, seats=random_cafe.seats)
    return jsonify(cafe=random_cafe.to_dict())

@app.route('/all')
def get_cafes():
    result = db.session.execute(db.select(Cafe))
    cafes = result.scalars().all()

    cafes_json = []
    for cafe in cafes:
        cafes_json.append(cafe.to_dict())
    return jsonify(cafes=cafes_json)

@app.route('/search')
def search_cafes():
    location = request.args.get('loc')
    result = db.session.execute(db.select(Cafe).where(Cafe.location == location))
    cafes = result.scalars().all()

    cafes_json = []
    for cafe in cafes:
        cafes_json.append(cafe.to_dict())

    if len(cafes_json) != 0:
        return jsonify(cafes=cafes_json)
    else:
        return jsonify(error='No cafes found at this location.')
    
## HTTP POST - Create Record

@app.route('/add', methods=['POST'])
def add_cafe():
    name = request.form['name']
    img_url = request.form['img_url']
    has_toilet = bool(request.form['has_toilet'])
    has_wifi = bool(request.form['has_wifi'])
    has_sockets = bool(request.form['has_sockets'])
    can_take_calls = bool(request.form['can_take_calls'])
    price = request.form['coffee_price']
    map_url = request.form['map_url']
    location = request.form['loc']
    seats=request.form['seats']

    new_cafe = Cafe(name=name, map_url=map_url, img_url=img_url, location=location, has_toilet=has_toilet, 
                    has_wifi=has_wifi, has_sockets=has_sockets, seats=seats,
                    can_take_calls=can_take_calls, coffee_price=price)
    
    db.session.add(new_cafe)
    db.session.commit()

    return jsonify(response={'success': "Succesfully added the new cafe."})

## HTTP PUT/PATCH - Update Record

@app.route('/update-price/<int:cafe_id>', methods=['PATCH'])
def update_price(cafe_id):

    new_price = request.args.get('new_price')
    cafe_to_update = db.get_or_404(Cafe, cafe_id)

    if cafe_to_update:
        cafe_to_update.coffee_price = new_price
        db.session.commit()
        return jsonify(success='The coffee price has been updated.')
    else:
        return jsonify(error={'Not found': 'The cafe you were looking for was not found!'}), 404

## HTTP DELETE - Delete Record

@app.route('/delete-cafe/<cafe_id>', methods=['DELETE'])
def delete_cafe(cafe_id):
    api_key = request.args.get('api_key')

    cafe = db.get_or_404(Cafe, cafe_id)

    if cafe:
        if api_key == 'TopSecretAPIKey':
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(success="Data has been sucessfully deleted")
        else:
            return jsonify(error='Make sure you enter the corect api_key')
    else:
        return jsonify(error={'Not found': 'The request cafe was not found'})

if __name__ == '__main__':
    app.run(debug=True)
