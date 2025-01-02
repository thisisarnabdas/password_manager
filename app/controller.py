from flask import Blueprint, render_template, url_for, redirect, flash, session, request
from app import db, ph
from app.forms import RegistrationForm, LoginForm, PasswordForm
from app.models import User, StoredPassword
from functools import wraps
from app.config import Config
import random
import string
from sqlalchemy.exc import IntegrityError

# Creates a Blueprint for the controller
controller = Blueprint('controller', __name__)


# Helper function for generating random passwords
def generate_random_password(length=16):
    """Generates a random password of the specified length."""
    characters = string.ascii_letters + string.digits + "!@#$%^&*()"
    return ''.join(random.choice(characters) for _ in range(length))


# Custom login required decorator
def login_required(f):
    """Decorator to require login for certain routes."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for("controller.login"))
        return f(*args, **kwargs)

    return decorated_function


@controller.route("/")
def home():
    """Home route that redirects based on login status."""
    if 'user_id' in session:
        return redirect(url_for("controller.dashboard"))
    return redirect(url_for("controller.login"))


@controller.route("/register", methods=['GET', 'POST'])
def register():
    """Handles user registration by validating and securely storing user information."""
    form = RegistrationForm()

    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'error')
            return redirect(url_for('controller.register'))

        new_user = User(username=form.username.data)
        new_user.set_password(form.password.data)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('controller.login'))
        except IntegrityError:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'error')

    return render_template('register.html', form=form)


@controller.route("/login", methods=['GET', 'POST'])
def login():
    """Handles user login."""
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            session.clear()
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for("controller.dashboard"))
        flash("Invalid username or password.", "danger")
    return render_template("login.html", form=form)


@controller.route("/logout")
def logout():
    """Logs out the user and clears session data."""
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("controller.login"))


@controller.route("/dashboard")
@login_required
def dashboard():
    """Displays the dashboard with decrypted stored passwords."""
    user = User.query.get(session.get('user_id'))
    if user is None:
        session.clear()
        flash("User not found. Please log in again.", "warning")
        return redirect(url_for("controller.login"))

    # Fetch stored passwords from the database
    stored_passwords = StoredPassword.query.filter_by(user_id=user.id).all()
    decrypted_passwords = []

    for password_entry in stored_passwords:
        # Debugging: Log fetched encrypted data
        print(f"Debug: Fetched Encrypted Password: {password_entry.encrypted_password}")

        # Decrypt the password
        decrypted_password = password_entry.decrypt_password()

        # Debugging: Log decrypted password
        print(f"Debug: Dashboard - Decrypted Password for {password_entry.title}: {decrypted_password}")

        decrypted_passwords.append({
            "id": password_entry.id,
            "title": password_entry.title,
            "username": password_entry.username,
            "url": password_entry.url,
            "password": decrypted_password,
            "created_at": password_entry.created_at
        })

    return render_template("dashboard.html", stored_passwords=decrypted_passwords)




@controller.route("/add_password", methods=['GET', 'POST'])
@login_required
def add_password():
    """Allows users to add new encrypted stored passwords."""
    form = PasswordForm()
    generated_password = None

    if 'generate_password' in request.form:
        generated_password = generate_random_password(16)
        form.password.data = generated_password

    if form.validate_on_submit() and 'submit' in request.form:
        user = User.query.get(session.get('user_id'))
        if not user:
            flash("User session expired. Please log in again.", "danger")
            return redirect(url_for("controller.login"))

        # Debugging: Log user and form data
        print(f"User: {user.username}, Form Data: {form.data}")

        password_entry = StoredPassword(
            title=form.title.data,
            username=form.username.data,
            url=form.url.data or None,
            user_id=user.id
        )

        try:
            # Debugging: Log before encryption
            print(f"Encrypting password for title: {form.title.data}")
            password_entry.encrypt_password(form.password.data)

            db.session.add(password_entry)
            db.session.commit()

            flash("Password stored successfully!", "success")
            return redirect(url_for("controller.dashboard"))
        except Exception as e:
            # Debugging: Log exception
            print(f"Failed to store password: {e}")
            db.session.rollback()
            flash("Failed to store password. Please try again.", "danger")

    return render_template("add_password.html", form=form, generated_password=generated_password)


@controller.route("/edit_password/<int:id>", methods=["GET", "POST"])
@login_required
def edit_password(id):
    """Allows users to edit an encrypted password entry."""
    password_entry = StoredPassword.query.get_or_404(id)
    user = User.query.get(session.get('user_id'))

    if not user or password_entry.user_id != user.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("controller.dashboard"))

    form = PasswordForm()

    # Pre-fill the title, username, password, and URL fields on GET request
    if request.method == "GET":
        form.title.data = password_entry.title
        form.username.data = password_entry.username
        form.url.data = password_entry.url
        form.password.data = password_entry.decrypt_password()

    if form.validate_on_submit():
        try:
            # Debugging: Log the form submission
            print(f"Debug: Submitted Title: {form.title.data}")
            print(f"Debug: Submitted Username: {form.username.data}")
            print(f"Debug: Submitted Password: {form.password.data}")
            print(f"Debug: Submitted URL: {form.url.data}")

            # Update the password entry with the new values
            password_entry.title = form.title.data
            password_entry.username = form.username.data
            password_entry.url = form.url.data or None

            # Encrypt the new password only if provided
            if form.password.data.strip():
                print("Debug: Encrypting new password.")
                password_entry.encrypt_password(form.password.data)
            else:
                print("Debug: No new password provided. Keeping current password.")

            db.session.commit()  # Save changes
            print("Debug: Password updated successfully.")
            flash("Password updated successfully!", "success")
            return redirect(url_for("controller.dashboard"))
        except Exception as e:
            db.session.rollback()
            print(f"Debug: Exception during password update: {e}")
            flash("Failed to update password. Please try again.", "danger")

    return render_template("edit_password.html", form=form, password_entry=password_entry)

@controller.route("/delete_password/<int:id>", methods=['POST'])
@login_required
def delete_password(id):
    """Deletes a stored password entry."""
    password_entry = StoredPassword.query.get_or_404(id)
    user_id = session.get('user_id')

    if not user_id or password_entry.user_id != user_id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("controller.dashboard"))

    try:
        db.session.delete(password_entry)
        db.session.commit()
        flash("Password deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash("Failed to delete password. Please try again.", "danger")

    return redirect(url_for("controller.dashboard"))
