from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import login_user, logout_user, current_user, login_required
from petopia.auth.models import User
from petopia import app, db

auth = Blueprint('auth', __name__, static_folder='templates/static', template_folder='templates/admin/')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            flash('Email already exists.', 'danger')
            return redirect(url_for('auth.register'))
        else:
            user = User(username=username, hash_password=password, is_superuser=True)
            db.session.add(user)
            db.session.commit()
            flash('Registered successfully!', 'success')
            return redirect(url_for('auth.logout'))
    return render_template('register.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('store.home'))

    if request.method == 'POST':
        print('POSTTTTT')
        username = request.form.get('username', None)
        password = request.form.get('password', None)

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password=password):
            login_user(user)
            return redirect('/admin')
        else:
            flash('Please check your username or password.', category='danger')
            return redirect(url_for('auth.login'))

    return render_template('login.html')


@auth.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
        return redirect('/admin')
    else:
        return redirect('/admin')
