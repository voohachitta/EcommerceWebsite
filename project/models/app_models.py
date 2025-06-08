from .. import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    cards = db.relationship('Card')
    ratings = db.relationship('Ratings')
    orders = db.relationship('Orders')
    address = db.relationship('Address')
    isUser = db.Column(db.Boolean, default=True)
    created_time = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_time = db.Column(db.DateTime(timezone=True), default=func.now())

class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(150))
    street = db.Column(db.String(150))
    street1 = db.Column(db.String(150))
    postal = db.Column(db.String(10))
    mobile = db.Column(db.String(150))
    state = db.Column(db.String(150))
    is_primary = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_time = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_time = db.Column(db.DateTime(timezone=True), default=func.now())

class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    created_time = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_time = db.Column(db.DateTime(timezone=True), default=func.now())

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    description = db.Column(db.String(1500))
    categories = db.relationship('Category')
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    created_time = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_time = db.Column(db.DateTime(timezone=True), default=func.now())

    def data(self):
        return {
            "name" : self.name,
            "description" : self.description,
            "categories" : [i.data() for i in self.categories]
        }

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    description = db.Column(db.String(1500))
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    items = db.relationship('Item')
    created_time = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_time = db.Column(db.DateTime(timezone=True), default=func.now())

    def data(self):
        return {
                    "id": self.id,
                    "name" : self.name
                }

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    description = db.Column(db.String(1500))
    url = db.Column(db.String(1500))
    price = db.Column(db.Float)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    ratings = db.relationship('Ratings')
    created_time = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_time = db.Column(db.DateTime(timezone=True), default=func.now())

class Ratings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer)
    description = db.Column(db.String(1500))
    likes = db.Column(db.Integer)
    dislikes = db.Column(db.Integer)
    price = db.Column(db.Float)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_time = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_time = db.Column(db.DateTime(timezone=True), default=func.now())

    def getUser(self):
        return User.query.filter_by(id = self.user_id).first()

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    cart_item = db.relationship('Cartitem')
    created = db.Column(db.DateTime(timezone=True), default=func.now())
    updated = db.Column(db.DateTime(timezone=True), default=func.now())

class Cartitem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'))
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    quantity = db.Column(db.Integer)
    total_price = db.Column(db.Float)
    status = db.Column(db.String(100))
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    created = db.Column(db.DateTime(timezone=True), default=func.now())
    updated = db.Column(db.DateTime(timezone=True), default=func.now())

    def getItem(self):
        return Item.query.filter_by(id = self.item_id).first()

class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(100))
    order_status = db.Column(db.String(100))
    user_email = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    cart_item = db.relationship('Cartitem')
    order_type = db.Column(db.String(100))
    payments = db.relationship('Payment')
    address_id = db.Column(db.Integer, db.ForeignKey('address.id'))
    created_time = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_time = db.Column(db.DateTime(timezone=True), default=func.now())

    def getAddress(self):
        return Address.query.filter_by(id = self.address_id).first()

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float)
    status = db.Column(db.String(15000))
    type = db.Column(db.String(15000))
    card_id = db.Column(db.Integer, db.ForeignKey('card.id'))
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    created_time = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_time = db.Column(db.DateTime(timezone=True), default=func.now())

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15000))
    number = db.Column(db.String(16))
    cvv = db.Column(db.String(4))
    validity = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    payments = db.relationship('Payment')

class PromoCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30))
    min_purchase = db.Column(db.Integer)
    discount = db.Column(db.Integer)
    status = db.Column(db.String(30))
    created_time = db.Column(db.DateTime(timezone=True), default=func.now())
    valid_till = db.Column(db.DateTime(timezone=True), default=func.now())