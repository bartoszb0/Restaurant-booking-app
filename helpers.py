from re import search
from flask import redirect, session, flash, request
from functools import wraps
from sqlalchemy.exc import IntegrityError
from models import db, Reservations
from datetime import datetime

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def error(message, path, category="danger"):
    flash(message, category)
    return redirect(path)


def validate(password):
    pattern = r"^(?=.*[A-Z])(?=.*[?!@#$%^&*])(?=.*[0-9])(?=.*[a-z])?.+$"
    if len(password) < 6:
        return False
    elif " " in password:
        return False
    elif not search(pattern, password):
        return False
    return True


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("role") != "admin":
            return redirect("/view")
        return f(*args, **kwargs)
    
    return decorated_function


def validate_reservations(path):

    reservation_id = request.form.get("reservation_id")
    if not reservation_id:
        return error("Missing reservation ID", path)

    # Ensure reservation_id is a valid integer
    try:
        reservation_id = int(reservation_id)
    except ValueError:
        return error("Invalid reservation ID", path)

    # Check if the reservation exists and belongs to the current user
    reservation = Reservations.query.get(reservation_id)
    if not reservation:
        return error("Reservation not found", path)
    if session["role"] == "user":
        if reservation.user_id != session["user_id"]:
            return error("You can only cancel your own reservations", path)

    try:
        db.session.delete(reservation)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return error("Error occured, reservation not cancelled", path)
    
    return True


def validate_date_time_guests(date, time, guests):
    GUESTS = list(range(2, 7))
    HOURS = list(range(10, 23))

    if not date or not time:
            return error("Missing input", "/view")
        
    date = datetime.strptime(date, "%Y-%m-%d").date()
    today = datetime.today().date()

    # Validate input, if user views date older than today
    if date <= today:
        return error("Invalid date", "/view")
    elif time not in HOURS:
        return error("Invalid time", "/view")
    elif guests not in GUESTS:
        return error("Invalid count of guests", "/view")
    
    return True