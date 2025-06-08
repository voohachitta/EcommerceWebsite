from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from werkzeug.exceptions import abort
from .models.app_models import Department, Category, Item, Orders, Payment, PromoCode
from flask_login import current_user
from . import db

import datetime

from project.auth import login_required

admin_bp = Blueprint('admin', __name__, url_prefix="/admin/")

@admin_bp.route('/')
@login_required
def index():
    departments = len(Department.query.all())
    categories = len(Category.query.all())
    items = len(Item.query.all())
    orders = len(Orders.query.all())
    payments = sum([i.amount for i in Payment.query.all()])
    return render_template('admin/dashboard.html', user=current_user, departments = departments, categories = categories, items = items, orders = orders, payments = payments)

@admin_bp.route('/add_department/', methods=["POST", "GET"])
@login_required
def add_department():
    if(request.method == 'POST'):
        name = request.form.get("dept_name")
        desc = request.form.get("dept_desc")
        department = Department.query.filter_by(name=name).first()
        if not department :
            new_department = Department(name=name, description=desc)
            db.session.add(new_department)
            db.session.commit()
            return redirect(url_for("admin.view_departments"))
    return render_template('admin/add_department.html', user=current_user)

@admin_bp.route('/add_category/', methods = ["POST", "GET"])
@login_required
def add_category():
    departments = Department.query.all()
    if(request.method == 'POST'):
        name = request.form.get("name")
        desc = request.form.get("description")
        dept_id = request.form.get("department")
        category = Category.query.filter_by(name=name).first()
        if not category :
            new_department = Category(name=name, description=desc, department_id=dept_id)
            db.session.add(new_department)
            db.session.commit()
            return redirect(url_for("admin.view_categories"))
    return render_template('admin/add_category.html', user=current_user, departments = departments)

@admin_bp.route("/getDepartment/<int:id>/")
@login_required
def getDepartmentById(id):
    data = jsonify(Department.query.filter_by(id = id).first().data())
    print(data)
    return data

@admin_bp.route('/add_item/', methods = ["GET", "POST"])
@login_required
def add_item():
    departments = Department.query.all()
    if(request.method == "POST"):
        data = request.form
        item = Item.query.filter_by(name = data.get("img_name")).first()
        print(data)
        if not item:
            print("Done ...")
            new_item = Item(name=data.get("img_name"), description=data.get("img_desc"), url=data.get("img_url"),
                            category_id=int(data.get("cat_id")), price=float(data.get("img_price")))
            db.session.add(new_item)
            db.session.commit()
            return redirect(url_for("admin.view_items"))
    return render_template('admin/add_item.html', user=current_user, departments = departments)

@admin_bp.route('/departments/')
@login_required
def view_departments():
    departments = Department.query.all()
    return render_template('admin/view_departments.html', user=current_user, departments = departments)

@admin_bp.route('/categories/')
@login_required
def view_categories():
    categories = Category.query.all()
    return render_template('admin/view_categories.html', user=current_user, categories = categories)

@admin_bp.route('/items/')
@login_required
def view_items():
    items = Item.query.all()
    return render_template('admin/view_items.html', user=current_user, items = items)

@admin_bp.route('/add_promocode/', methods = ["GET", "POST"])
@login_required
def add_promocode():
    if(request.method == "POST"):
        data = request.form
        promo = PromoCode.query.filter_by(code = data.get("code")).first()
        print(data)
        print(promo)
        if not promo:
            print(data)
            new_promo = PromoCode(code = data.get("code"),
                                  min_purchase = data.get("min_val"),
                                  discount = data.get("discount"),
                                  valid_till = datetime.datetime.strptime(data.get("valid_till"), "%Y-%M-%d"),
                                  status = "ACTIVE")
            db.session.add(new_promo)
            db.session.commit()
            print(new_promo)
            return redirect(url_for("admin.view_promocodes"))

    return render_template('admin/add_promocode.html', user=current_user)

@admin_bp.route('/promocodes/')
@login_required
def view_promocodes():
    codes = PromoCode.query.all()
    return render_template('admin/view_promocodes.html', user=current_user, codes = codes)

@admin_bp.route('/orders/')
@login_required
def orders():
    orders = Orders.query.all()
    return render_template('admin/view_orders.html', user=current_user, orders = orders)

@admin_bp.route('/orders/<status>/')
@login_required
def orders_with_status(status):
    orders = Orders.query.filter_by(order_status = status).all()
    return render_template('admin/view_orders.html', user=current_user, orders = orders)

@admin_bp.route('/update_status/', methods = ["POST"])
@login_required
def update_status():
    if(request.method == "POST"):
        data = request.get_json()
        print(data)
        order = Orders.query.filter_by(id = data["order_id"]).first()
        order.order_status = data["status"]
        db.session.commit()
        return {"status" : "true"}
    return {"status" : "false"}