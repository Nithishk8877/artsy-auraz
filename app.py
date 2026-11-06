import os
from flask import Flask, render_template, request, session, redirect
from flask_cors import CORS
from models import db, Category
from routes.products import products_bp
from routes.customers import customers_bp
from routes.orders import orders_bp
from auth import admin_required, ADMIN_PASSWORD
from routes.uploads import uploads_bp
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///artsy_auraz.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = os.environ.get("SECRET_KEY", "artsy-auraz-change-this-key")
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # max 5 MB photo

CORS(app)
db.init_app(app)
app.register_blueprint(products_bp)
app.register_blueprint(customers_bp)
app.register_blueprint(orders_bp)
app.register_blueprint(uploads_bp)
CATEGORIES = [
    "Resin Keychains",
    "Handwritten Letters",
    "Resin Coasters",
    "Scrapbooks",
    "Satin Ribbon Flower Bouquets",
    "Pipe Cleaner Flower Bouquets",
    "Customized Hampers",
    "Rose Preservation in Resin",
]

with app.app_context():
    db.create_all()
    if Category.query.count() == 0:
        for name in CATEGORIES:
            db.session.add(Category(name=name))
        db.session.commit()


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/admin")
@admin_required
def admin():
    return render_template("admin.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["is_admin"] = True
            return redirect("/admin")
        error = "Wrong password"
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)