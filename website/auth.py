import os
from flask import Blueprint, flash, render_template, request, url_for, redirect, current_app
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from .models import User
from .forms import LoginForm, RegisterForm, ProfileEditForm
from . import db, bcrypt

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
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

        image_file = form.profile_image.data
        if image_file:
            filename = secure_filename(image_file.filename)
            upload_folder = os.path.join(current_app.root_path, 'static/img')
            os.makedirs(upload_folder, exist_ok=True)
            image_path = os.path.join(upload_folder, filename)
            image_file.save(image_path)
            profile_image_path = f'img/{filename}'
        else:
            profile_image_path = 'img/default_avatar.png'

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = User(
            username=username,
            password_hash=hashed_password,
            email=email,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone_number=form.phone_number.data,
            street_address=form.street_address.data,
            gender=form.gender.data,
            profile_image=profile_image_path
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful. You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('user.html', form=form, heading='Register')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
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

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileEditForm(obj=current_user)

    if form.validate_on_submit():
        if form.username.data != current_user.username:
            if db.session.scalar(db.select(User).where(User.username == form.username.data)):
                flash("Username already taken.", "danger")
                return redirect(url_for('auth.profile'))

        if form.email.data != current_user.email:
            if db.session.scalar(db.select(User).where(User.email == form.email.data)):
                flash("Email already in use.", "danger")
                return redirect(url_for('auth.profile'))

        image_file = form.profile_image.data
        if image_file and hasattr(image_file, 'filename') and image_file.filename != '':
            filename = secure_filename(image_file.filename)
            upload_folder = os.path.join(current_app.root_path, 'static/img')
            os.makedirs(upload_folder, exist_ok=True)
            image_path = os.path.join(upload_folder, filename)
            image_file.save(image_path)
            current_user.profile_image = f'img/{filename}'

        if form.password.data:
            current_user.password_hash = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.phone_number = form.phone_number.data
        current_user.street_address = form.street_address.data
        current_user.gender = form.gender.data

        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for('auth.profile'))

    return render_template('profile.html', form=form, heading="Edit Profile")