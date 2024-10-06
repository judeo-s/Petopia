from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_cors import cross_origin
from plant.shop.models import Product
from flask_login import login_user, logout_user, current_user, login_required
from plant.core.models import User

core = Blueprint('core', __name__, static_folder='static')


@core.route('/')
def home():
    products = Product.query.all()[:8]
    return render_template('home.html', products=products)


@core.route('/admin/login', methods=['GET', 'POST'])
@cross_origin()
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', None)
        password = request.form.get('password', None)

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password=password):
            login_user(user)
            return redirect(url_for('core.admin_dashboard'))
        else:
            flash('Please check your username or password.', category='danger')
            return redirect(url_for('core.admin_login'))
    if request.method == 'GET':
        return render_template('admin/login.html')


@core.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('core.admin_login'))


@core.route('/admin/dashboard')
@login_required
def admin_dashboard():
    return render_template('admin/dashboard.html')


@core.route('/admin/products')
@login_required
def admin_products():
    return render_template('admin/products.html')


@core.route('/admin/categories')
@login_required
def admin_categories():
    return render_template('admin/categories.html')


@core.route('/admin/orders')
@login_required
def admin_orders():
    return render_template('admin/orders.html')


@core.route('/admin/media')
@login_required
def admin_media():
    return render_template('admin/media.html')
