import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from datetime import datetime
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, pound, array_merge



# Configure application
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///shop.db")

app.jinja_env.filters["pound"] = pound

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)



@app.route("/", methods=["GET", "POST"])
def index():
    available_sizes = {11, 12, 13, 14, 15, 16, 17, 18, 19}
    try:
        items = db.execute("SELECT * FROM items ORDER BY RANDOM() LIMIT 100;")
        return render_template("index.html", items=items, available_sizes=available_sizes)
    except Exception as e:
        print(e)

@app.route("/product/")
@app.route("/product/<_type>/")
@app.route("/product/<_type>/<_material>")
def products(_type, _material=''):
    available_sizes = {11, 12, 13, 14, 15, 16, 17, 18, 19}

    _type = str(_type)
    _material = str(_material)
    try:
        if _material == '':
            items = db.execute("SELECT * FROM items WHERE type = ?", _type)
            return render_template("index.html", items=items, available_sizes=available_sizes, current_type=_type)
        items = db.execute("SELECT * FROM items WHERE material = ? AND type = ? ORDER BY RANDOM() LIMIT 100;", _material, _type)
        return render_template("index.html", items=items, available_sizes=available_sizes, current_type=_type)
    except Exception as e:
        print(e)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash('Must provide username', 'alert alert-danger text-center')
            return render_template("login.html")


        # Ensure password was submitted
        elif not request.form.get("password"):
            flash('Must provide password', 'alert alert-danger text-center')
            return render_template("login.html")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash('Wrong username or password', 'alert alert-danger text-center')
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":
        username = request.form.get("username")
        # Check if the username already exists
        check_database = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(check_database) != 0:
            flash('User already exists', 'alert alert-primary-red text-center')
            return render_template("register.html")
        # Check if the Username field wasn't left empty
        if not username:
            flash('Username cannot be empty', 'alert alert-danger text-center')
            return render_template("register.html")

        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if password != confirmation:
            flash('Password doesnt match', 'alert alert-danger text-center')
            return render_template("register.html")
        if not password:
            flash('Password cannot be empty', 'alert alert-danger text-center')
            return render_template("register.html")
        passwordhash = generate_password_hash(password, method='pbkdf2:sha256')
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, passwordhash)
        return redirect("/")

    return render_template("register.html")

@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    """ Let the user change his account settings """

    if request.method == "POST":
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        if not check_password_hash(rows[0]["hash"], request.form.get("oldpassword")):
            flash('Wrong password', 'alert alert-danger text-center')
            return render_template("account.html")
        if password != confirmation:
            flash('Password doesnt match', 'alert alert-danger text-center')
            return render_template("account.html")
        if not password:
            flash('Password cannot be empty', 'alert alert-danger text-center')
            return render_template("account.html")
        passwordhash = generate_password_hash(password, method='pbkdf2:sha256')
        db.execute("UPDATE users SET hash = ? WHERE id = ?", passwordhash, session["user_id"])
        flash('Password changed', 'alert alert-primary border text-center')
        return redirect("/")
    return render_template("account.html")

@app.route("/add", methods=["POST"])
def add_item_to_basket():
    try:
        quantity = int(request.form["quantity"])
        _id = request.form["id"]
        if quantity and _id and  request.method == 'POST':
            asd = db.execute("SELECT * FROM items WHERE id=?", _id)
            row = asd[0]
            itemArray = { row['id'] : {'name' : row['itemname'], 'id' : row['id'], 'quantity' : quantity, 'price' : row['price'], 'image' : row['img'], 'total_price': quantity * row['price']}}
            totalPrice = 0
            totalQuantity = 0
            session.modified = True
            print(session)
            if 'basket_item' in session:
                if row['id'] in session['basket_item']:
                    for key, value in session['basket_item'].items():
                        if row['id'] == key:
                            old_quantity = session['basket_item'][key]['quantity']
                            total_quantity = old_quantity + quantity
                            session['basket_item'][key]['quantity'] = total_quantity
                            session['basket_item'][key]['total_price'] = total_quantity * row['price']
                else:
                    session['basket_item'] = array_merge(session['basket_item'], itemArray)
                for key, value in session['basket_item'].items():
                    individual_quantity = int(session['basket_item'][key]['quantity'])
                    individual_price = float(session['basket_item'][key]['total_price'])
                    totalQuantity = totalQuantity + individual_quantity
                    totalPrice = totalPrice + individual_price
            else:
                session['basket_item'] = itemArray
                totalQuantity = totalQuantity + quantity
                totalPrice = totalPrice + quantity * row['price']
            session['totalQuantity'] = totalQuantity
            session['totalPrice'] = totalPrice

            #flash('Added', 'alert alert-primary border text-center')
            return redirect("/")
        else:
            return 'Error while adding item to cart'

    except Exception as e:
        print(e)


@app.route('/empty')
def empty_basket():
    try:
        del session['basket_item']
        del session['totalQuantity']
        del session['totalPrice']
        return redirect("/")
    except Exception as e:
        print(e)

@app.route('/delete/<int:_id>')
def delete_product(_id):
    modal = 1
    try:
        totalPrice = 0
        totalQuantity = 0
        session.modified = True
        for item in session['basket_item']:
            if item == _id:
                session['basket_item'].pop(item, None)
                if 'basket_item' in session:
                    for key, value in session['basket_item'].items():
                        individual_quantity = int(session['basket_item'][key]['quantity'])
                        individual_price = float(session['basket_item'][key]['total_price'])
                        totalQuantity = totalQuantity + individual_quantity
                        totalPrice = totalPrice + individual_price
                break
        if totalQuantity == 0:
            del session['basket_item']
            del session['totalQuantity']
            del session['totalPrice']
            return redirect("/")
        else:
            session['totalQuantity'] = totalQuantity
            session['totalPrice'] = totalPrice
        return redirect("/")
    except Exception as e:
        print(e)

@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():

    print(int(session['totalPrice']))
    if int(session['totalPrice']) > 100:
        fee = 0
    else:
        fee = 5
    return render_template("checkout.html", fee=fee)

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)