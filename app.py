from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc
from datetime import datetime

from helpers import login_required, error, validate, admin_required, validate_reservations, validate_date_time_guests
from models import db, Users, Reservations

app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = "your_secret_key"
Session(app)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Create database file and tables
with app.app_context():
    db.create_all()

# Create admin profile
with app.app_context():
    if not Users.query.filter_by(role="admin").first():
        admin = Users(username="admin", password_hash=generate_password_hash("123"), role="admin")
        db.session.add(admin)
        db.session.commit()


@app.route("/")
def index():
    return redirect("/view")


@app.route("/login", methods=["GET", "POST"])
def login():
    # Forget any user_id, save flashes before they are cleared so they can appear
    flashes = session.get("_flashes", [])  # Save flash messages before clearing session
    session.clear()  # Clear session completely
    session["_flashes"] = flashes

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return error("Missing name and/or password", "/login")
        
        user = Users.query.filter_by(username=username).first() # go to Notion for explanation | SELECT * FROM users WHERE username=username LIMIT 1;

        if user is None:
            return error("Account with such name doesn't exist", "/login")
        elif not check_password_hash(user.password_hash, password):
            return error("Wrong password", "/login")

        session["role"] = user.role
        session["user_id"] = user.id
        flash("Logged in", "success")
        return redirect("/")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username or not password or not confirmation:
            return error("Missing username and/or password and/or confirmation password", "/register")
        elif len(username) > 16:
            return error("Max length of username is 16 characters", "/register")
        elif not validate(password):
            return error("Password must be at least 6 characters long and contain at least: one uppercase letter, one digit, one special character and can't include spacebar", "/register")
        elif password != confirmation:
            return error("Password do not match", "/register")

        # Hash password
        password = generate_password_hash(password)

        # Create a new user and add to the database
        new_user = Users(username=username, password_hash=password) # INSERT INTO users (username, hash) VALUES (username, password)
        try:
            db.session.add(new_user)
            db.session.commit() # Save changes to database
        except IntegrityError: # If there is user with such name
            db.session.rollback() # Undo changes to database
            return error("Account with such name already exists", "/register")
        
        flash("Account created", "success")
        return redirect("/login")

    return render_template("register.html")


@app.route("/logout")
@login_required
def logout():
    session.clear() # Forget any user_id
    flash("Logged out", "success")
    return redirect("/login") # Redirect user to login form


@app.route("/view", methods = ["GET", "POST"])
def view():
    if request.method == "POST":
        tables = {
            2: 4,  # Tables available for 2 guests
            3: 3,  # Tables available for 3 guests
            4: 5,  # Tables available for 4 guests
            5: 3,  # Tables available for 5 guests
            6: 6,  # Tables available for 6 guests
        }

        date = request.form.get("date")
        time = int(request.form.get("time"))
        guests = int(request.form.get("guests"))

        validation_result = validate_date_time_guests(date, time, guests)
        if validation_result is not True:
            return validation_result

        # LOOK FOR TABLES WITH SUCH COUNT AND TIME THAT ARE AVAILABLE AND PASS THEM TO HTML
        reservations = Reservations.query.filter_by(date=date, time=time, guests=guests).all()

        # Reservations is a list of available tables
        if len(reservations) < tables[guests]:
            return render_template("viewed.html", date=date, time=time, guests=guests, reservations=(tables[guests] - len(reservations)))
        else:
            return error(f"No tables are available on {date}, {time}:00 for {guests} people", "view")
        
    else:
        return render_template("view.html")


@app.route("/book", methods = ["GET", "POST"])
@login_required
def book():
    if request.method == "POST":

        date = request.form.get("date")
        time = int(request.form.get("time"))
        guests = int(request.form.get("guests"))

        validation_result = validate_date_time_guests(date, time, guests)
        if validation_result is not True:
            return validation_result


        # Handle booking table
        new_reservation = Reservations(date=date, time=time, guests=guests, user_id=session["user_id"])
        try:
            db.session.add(new_reservation)
            db.session.commit() # Save changes to database
        except IntegrityError: # If there is user with such name
            db.session.rollback() # Undo changes to database
            return error("Error occured, table not booked", "/view")


        flash("Table booked", "success")
        return redirect("/reservations")
    
    else:
        return redirect("/view")


@app.route("/reservations", methods = ["GET", "POST"])
@login_required
def reservations():
    # To display all reservations via GET
    reservations = Reservations.query.filter_by(user_id=session["user_id"]).order_by(desc(Reservations.date)).all()

    if request.method == "POST":

        if session["role"] == "admin":
            path = "/all_reservations"
        else:
            path = "/reservations"

        if validate_reservations(path):
            flash("Reservation cancelled", "success")
            return redirect(path)
    
    else:
        return render_template("reservations.html", reservations=reservations)


@app.route("/all_reservations")
@login_required
@admin_required
def all_reservations():
    all_reservations =  Reservations.query.all()
    return render_template("reservations.html", reservations=all_reservations)

@app.route("/change_password", methods = ["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        user = Users.query.get(session["user_id"])

        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        confirmation = request.form.get("confirmation")

        if not old_password or not new_password or not confirmation:
            return error("Invalid input", "/change_password")
        elif not check_password_hash(user.password_hash, old_password):
            return error("Old password is invalid", "/change_password")
        elif new_password != confirmation:
            return error("New password and confirmation password are not the same", "/change_password")
        elif not validate(new_password):
            return error("Password must be at least 6 characters long and contain at least: one uppercase letter, one digit, one special character and can't include spacebar", "/register")

        new_password = generate_password_hash(new_password)
        user.password_hash = new_password
        db.session.commit()


        flash("Password changed", "success")
        return redirect("/change_password")
    else:
        return render_template("change_password.html")


if __name__ == "__main__":
    app.run(debug=True)
