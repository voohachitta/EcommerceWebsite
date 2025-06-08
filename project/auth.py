from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, session
from .models.app_models import User, Admin, Cart, Address, Card
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
import uuid
import datetime

auth = Blueprint('auth', __name__, url_prefix="/auth")

@auth.route('/login/', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        email = request.form.get('username')
        password = request.form.get('password')
        type = request.form.get('type')

        if(type == 'ADMIN'):
            print("Admin ---->")
            user = Admin.query.filter_by(email=email).first()
            template = "admin.index"
        else:
            user = User.query.filter_by(email=email).first()
            template = "app.index"
        print(user, template, email, password)
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                session.permanent = True
                session['type'] = 'admin' if(type == 'ADMIN') else 'user'
                print('Logged in successfully! success', template)
                return redirect(url_for(template))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("auth/login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/get_admins/')
def get_admins():
    return jsonify([{i.email:i.password} for i in Admin.query.all()])
@auth.route('/create_admin/', methods=['GET', 'POST'])
def create_admin():
    if request.method == "GET":
        email = request.args.get("email")
        password = generate_password_hash(
                request.args.get("pass"))
        admin = Admin(email = email, password = password)
        db.session.add(admin)
        db.session.commit()
        return "Account Created !"
@auth.route('/sign_up/', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('username')
        first_name = request.form.get('fname')
        last_name = request.form.get('lname')
        password1 = request.form.get('password')
        password2 = request.form.get('password1')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(
                password1), last_name=last_name)
            db.session.add(new_user)
            user_data = User.query.filter_by(email=new_user.email).first()
            new_address = Address(street=request.form.get("a_addr_1"),
                                  street1=request.form.get("a_addr_2"),
                                  state=request.form.get("a_state"),
                                  postal=request.form.get("a_zip"),
                                  country=request.form.get("a_country"),
                                  mobile=request.form.get("a_phone"),
                                  user_id=user_data.id,
                                  is_primary=True)
            new_card = Card(name = new_user.first_name.upper(),
                            number = request.form.get("cc_no"),
                            cvv = request.form.get("cc_cvv"),
                            validity = datetime.datetime.strptime(f'{request.form.get("cc_val")}-01', "%Y-%M-%d"),
                            user_id = user_data.id)
            db.session.add(new_address)
            db.session.add(new_card)
            cart = Cart(user_id=user_data.id)
            db.session.add(cart)
            db.session.commit()
            login_user(new_user, remember=True)
            session.permanent = True
            session['type'] = 'user'
            flash('Account created!', category='success')
            return redirect(url_for('app.index'))

    return render_template("auth/register.html", user=current_user)

@auth.route('/guest_login/', methods=['GET', 'POST'])
def guest_sign_up():
    if request.method == 'POST':
        uid = uuid.uuid1()
        new_user = User(email=f"{uid.hex}@fusionmart.com", first_name=str(uid).split("-")[0], password=generate_password_hash(
                str(uuid)), last_name=str(uid).split("-")[0][-1], isUser=False)
        db.session.add(new_user)
        user_data = User.query.filter_by(email=new_user.email).first()
        cart = Cart(user_id=user_data.id)
        db.session.add(cart)
        db.session.commit()
        login_user(user_data, remember=True)
        session.permanent = True
        session['type'] = 'user'
        flash('Account created!', category='success')
        flash('Guest Account created!', category='success')
        return redirect(url_for('app.index'))

    return render_template("auth/register.html", user=current_user)