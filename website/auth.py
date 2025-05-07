from flask import Blueprint, flash, render_template, request, url_for, redirect
from flask_login import login_user, login_required, logout_user
from .models import User
from .forms import LoginForm, RegisterForm
from . import db, bcrypt

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.user_name.data
        password = form.password.data
        email = form.email.data

        existing_user = db.session.scalar(db.select(User).where(User.username == username))
        if existing_user:
            flash('Username already exists. Please try another.', 'warning')
            return redirect(url_for('auth.register'))

        existing_email = db.session.scalar(db.select(User).where(User.email == email))
        if existing_email:
            flash('Email already registered. Please use a different one.', 'warning')
            return redirect(url_for('auth.register'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, password_hash=hashed_password, email=email)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful. You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('user.html', form=form, heading='Register')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.user_name.data
        password = form.password.data
        user = db.session.scalar(db.select(User).where(User.username == username))

        if user is None:
            flash('Invalid username.', 'danger')
        elif not bcrypt.check_password_hash(user.password_hash, password):
            flash('Invalid password.', 'danger')
        else:
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('main.index'))

    return render_template('user.html', form=form, heading='Login')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))