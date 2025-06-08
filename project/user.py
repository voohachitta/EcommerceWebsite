import datetime

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
import uuid

from . import db

from itertools import chain

from .models.app_models import Department, Cart, Cartitem, Item, PromoCode, Address, Card, Orders, Payment, Ratings, Category

from project.auth import login_required, current_user

app_bp = Blueprint('app', __name__)

@app_bp.route('/')
def index():
    print(current_user)
    departments = Department.query.all()
    data = {i:list(chain(*[j.items for j in i.categories])) for i in departments}
    print(data)
    if(not current_user.is_authenticated):
        shopping_cart = None
    else:
        shopping_cart = Cart.query.filter_by(user_id = current_user.id).first()
    cart_items = list(filter(lambda x : x.status == 'ACTIVE', shopping_cart.cart_item)) if(shopping_cart is not None) else []
    return render_template('user/index.html', departments=data, cart_items = len(cart_items),
                           item_ids = [i.item_id for i in cart_items], user = current_user)

@app_bp.route('/cart', methods = ["POST", "GET"])
@login_required
def cart():
    if(request.method == "POST"):
        print("Got !")
        item_id = request.form.get("item_id")
        shopping_cart = Cart.query.filter_by(user_id = current_user.id).first()
        item = Cartitem.query.filter_by(item_id = item_id)\
            .filter_by(cart_id = shopping_cart.id).filter_by(status = 'ACTIVE').first()
        if not item:
            new_item = Cartitem(cart_id = shopping_cart.id,
                                item_id = item_id,
                                quantity = int(request.form.get("item_quantity")),
                                total_price = int(request.form.get("item_quantity")) * float(request.form.get("item_price")),
                                status = 'ACTIVE')
            db.session.add(new_item)
            db.session.commit()
    shopping_cart = Cart.query.filter_by(user_id = current_user.id).first()
    cart_items = list(filter(lambda x : x.status == 'ACTIVE', shopping_cart.cart_item))
    cart_response = {Item.query.filter_by(id = i.item_id) : i for i in cart_items}
    print(cart_response)
    return render_template("user/shopping_cart.html", cart_response = cart_response, cart_items = len(cart_items), user = current_user)


@app_bp.route('/item/<id>/')
@login_required
def item(id):
    if (not current_user.is_authenticated):
        shopping_cart = None
    else:
        shopping_cart = Cart.query.filter_by(user_id=current_user.id).first()
    cart_items = list(filter(lambda x: x.status == 'ACTIVE', shopping_cart.cart_item)) if (
                shopping_cart is not None) else []
    item = Item.query.filter_by(id = id).first()
    return render_template("user/item.html", user = current_user, item = item, item_ids = [i.item_id for i in cart_items], cart_items = len(cart_items))

@app_bp.route('/checkout/', methods = ["GET", "POST"])
@login_required
def checkout():
    data = None
    if (not current_user.is_authenticated):
        shopping_cart = None
    else:
        shopping_cart = Cart.query.filter_by(user_id=current_user.id).first()
        data = request.form.get("pickup")
    cart_items = list(filter(lambda x: x.status == 'ACTIVE', shopping_cart.cart_item)) if (
                shopping_cart is not None) else []
    cart_response = {Item.query.filter_by(id = i.item_id) : i for i in cart_items}
    existing_addr = Address.query.filter_by(user_id=current_user.id).all()
    card_data = Card.query.filter_by(user_id = current_user.id).first()
    print(data)
    return render_template("user/checkout.html", user = current_user, item_ids = [i.item_id for i in cart_items], cart_response = cart_response, addresses = existing_addr, card = card_data, is_store_pickup = (data == "store"), cart_items = len(cart_items))

@app_bp.route('/items_filter/')
@login_required
def items_filter():
    if (not current_user.is_authenticated):
        shopping_cart = None
    else:
        shopping_cart = Cart.query.filter_by(user_id=current_user.id).first()
    cart_items = list(filter(lambda x: x.status == 'ACTIVE', shopping_cart.cart_item)) if (
                shopping_cart is not None) else []
    items = Item.query.all()
    departments = Department.query.all()
    return render_template("user/items_filter.html", user = current_user, items = items, item_ids = [i.item_id for i in cart_items], departments = departments, cart_items = len(cart_items))

@app_bp.route('/itemsByCategory/<int:category_id>/', methods = ["POST", "GET"])
def getItemIdsByCategory(category_id):
    try:
        category = Category.query.filter_by(id = category_id).first()
        return {
            "status" : "true",
            "item_ids" : [i.id for i in category.items]
        }
    except Exception as e:
        return {
            "status" : "false"
        }


@app_bp.route('/deleteItem/<id>/')
@login_required
def delete_item(id):
    if (not current_user.is_authenticated):
        shopping_cart = None
    else:
        shopping_cart = Cart.query.filter_by(user_id=current_user.id).first()
        cart_item = Cartitem.query.filter_by(id = int(id)).first()
        print(cart_item)
        db.session.delete(cart_item)
        db.session.commit()
    cart_items = list(filter(lambda x : x.status == 'ACTIVE', shopping_cart.cart_item))
    cart_response = {Item.query.filter_by(id = i.item_id) : i for i in cart_items}
    print(cart_response)
    return render_template("user/shopping_cart.html", cart_response = cart_response, cart_items = len(cart_items))


@app_bp.route('/updateQty/', methods = ["POST"])
@login_required
def updateCart():
    if(request.method == "POST"):
        data = request.get_json()
        cartItem = Cartitem.query.filter_by(id = data["cid"]).first()
        item = Item.query.filter_by(id = cartItem.item_id).first()
        print(cartItem)
        cartItem.quantity = int(data["iqty"])
        cartItem.total_price = float(item.price) * int(data["iqty"])
        db.session.commit()
    return "200"

@app_bp.route('/verifyCoupon/', methods = ["POST"])
@login_required
def verifyCoupon():
    if(request.method == "POST"):
        data = request.get_json()
        code = PromoCode.query.filter_by(code = data["code"]).first()
        print(code, data)
        if code:
            print(datetime.datetime.now(), code.valid_till)
            if(datetime.datetime.now() <= code.valid_till):
                return {"status" : "true", "value" : code.code, "purchase_val" : code.min_purchase, "discount" : code.discount, "id" : code.id}
            return {"status" : "false"}
    return {"status" : "false"}

@app_bp.route('/profile/', methods = ["GET", "POST"])
@login_required
def profile():
    existing_addr = Address.query.filter_by(user_id=current_user.id).all()
    card_data = Card.query.filter_by(user_id = current_user.id).first()
    shopping_cart = Cart.query.filter_by(user_id = current_user.id).first()
    cart_items = list(filter(lambda x : x.status == 'ACTIVE', shopping_cart.cart_item)) if(shopping_cart is not None) else []
    return render_template("user/profile.html", user = current_user, addresses = existing_addr, card = card_data, cart_items= len(cart_items))

@app_bp.route('/add_address/', methods = ["POST"])
@login_required
def add_address():
    if(request.method == "POST"):
        data = request.get_json()
        data = {i:data[i].strip() for i in data}
        address = Address.query.filter_by(street = data["address1"])\
            .filter_by(street1 = data["address2"]).filter_by(state = data["state"])\
            .filter_by(postal = data["postal"])\
            .filter_by(country = data["country"])\
            .filter_by(mobile = data["phone"]).first()
        print(current_user.id, current_user)
        existing_addr = Address.query.filter_by(user_id = current_user.id).all()
        if not address :
            new_address = Address(street = data["address1"],
                                  street1 = data["address2"],
                                  state = data["state"],
                                  postal = data["postal"],
                                  country = data["country"],
                                  mobile = data["phone"],
                                  user_id = current_user.id,
                                  is_primary = len(existing_addr) == 0)
            db.session.add(new_address)
            db.session.commit()
            return {"msg" : "Success !"}
        return {"msg" :"Failed !"}
    return {"msg" :"Failed !"}

@app_bp.route("/add_card/", methods = ["POST"])
def add_card():
    if(request.method == "POST"):
        card_data = request.get_json()
        print(card_data)
        card = Card.query.filter_by(user_id = current_user.id, number = card_data["num"]).first()
        if not card:
            new_card = Card(name = current_user.first_name.upper(),
                            number = card_data["num"],
                            cvv = card_data["cvv"],
                            validity = datetime.datetime.strptime(f'{card_data["validity"]}-01', "%Y-%M-%d"),
                            user_id = current_user.id)
            db.session.add(new_card)
            db.session.commit()
            return {"status" : "Added !"}
        return {"status" : "Not Added !"}
    return {"status" : "Not Added !"}

@app_bp.route("/place_order/", methods = ["POST"])
def place_order():
    if(request.method == "POST"):
        checkout_details = request.get_json()
        print(checkout_details)
        print(current_user.isUser)
        address = Address.query.filter_by(id = int(checkout_details["addr_id"])).first()
        print(address)
        if not address :
            address = Address(street = checkout_details["address"],
                                  street1 = checkout_details["address1"],
                                  state = checkout_details["state"],
                                  postal = checkout_details["zip"],
                                  country = checkout_details["country"],
                                  mobile = checkout_details["phone"],
                                  user_id = current_user.id,
                                  is_primary = False)
            print(address)
            db.session.add(address)
            db.session.commit()
        order = Orders(order_id = str(uuid.uuid1()),
                       order_status = "PLACED",
                       user_email = checkout_details["email"],
                       user_id = current_user.id,
                       order_type = "HOME_DELIVERY" if(checkout_details['store_pickup'] == 'False') else "STORE",
                       address_id = address.id)
        db.session.add(order)
        db.session.commit()
        shopping_cart = Cart.query.filter_by(user_id=current_user.id).first()
        cart_items = list(filter(lambda x: x.status == 'ACTIVE', shopping_cart.cart_item))
        for cart_item in cart_items:
            cart_item.status = "INACTIVE"
            cart_item.order_id = order.id
            cart_item.updated = datetime.datetime.now()
        card = Card.query.filter_by(id = checkout_details["cc_id"]).first()
        if not card:
            card = Card(name = current_user.first_name.upper(),
                        number = checkout_details["ccno"],
                        cvv = checkout_details["cccvv"],
                        validity = datetime.datetime.strptime(f'{checkout_details["ccval"]}-01', "%Y-%M-%d"),
                        user_id = current_user.id)
            db.session.add(card)
            db.session.commit()
        if(checkout_details["coupon_id"] != "9999"):
            coupon = PromoCode.query.filter_by(id = checkout_details["coupon_id"]).first()
            coupon.status = "INACTIVE"
        payments = Payment(amount=float(checkout_details["total"]),
                           status="PAID",
                           type="CARD",
                           card_id=card.id,
                           order_id=order.id)
        db.session.add(payments)
        db.session.commit()

        shopping_cart = Cart.query.filter_by(user_id=current_user.id).first()
        cart_items = list(filter(lambda x: x.status == 'ACTIVE', shopping_cart.cart_item)) if (shopping_cart is not None) else []
        return {"status": "true", "order_id": order.order_id}
    return {"status" : "false"}

@app_bp.route("/order_success/<oid>/")
def order_success(oid):
    return render_template("user/thank_you.html", order_id=oid, user = current_user)

@app_bp.route("/my_orders/")
def my_orders():
    orders = Orders.query.filter_by(user_id = current_user.id).all()
    shopping_cart = Cart.query.filter_by(user_id = current_user.id).first()
    cart_items = list(filter(lambda x : x.status == 'ACTIVE', shopping_cart.cart_item)) if(shopping_cart is not None) else []
    return render_template("user/my_orders.html", user = current_user, orders = orders, cart_items = len(cart_items))

@app_bp.route("/add_rating/", methods = ["POST"])
def add_rating():
    if(request.method == "POST"):
        data = request.get_json()
        rating = Ratings(item_id = data["item_id"],
                         user_id = current_user.id,
                         score = int(data["rating"]),
                         description = data["description"])
        db.session.add(rating)
        db.session.commit()
        return {"status" : "true"}
    return {"status" : "false"}

@app_bp.route('/track_order/', methods = ["POST", "GET"])
def track_order():
    if(request.method == "POST"):
        order_id = request.form.get("order_id")
        order = Orders.query.filter_by(order_id = order_id).first()
        print(order)
        if order:
            return render_template("user/track_order_detail.html", user = current_user, order = order)
        return render_template("user/track_order.html", user = current_user, data = f"No order found with Order ID - {order_id}")
    return render_template("user/track_order.html", user = current_user)