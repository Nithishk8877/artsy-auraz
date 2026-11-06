from flask import Blueprint, request, jsonify
from models import db, Product, Category, OrderItem
from auth import check_admin

products_bp = Blueprint("products", __name__)


@products_bp.before_request
def require_admin_for_changes():
    # Paakkradhu (GET) public. Add/edit/delete admin mattum.
    if request.method in ("POST", "PUT", "DELETE"):
        return check_admin()


@products_bp.route("/api/categories", methods=["GET"])
def get_categories():
    categories = Category.query.all()
    return jsonify([c.to_dict() for c in categories])


@products_bp.route("/api/products", methods=["GET"])
def get_products():
    query = Product.query

    category_id = request.args.get("category_id")
    if category_id:
        query = query.filter_by(category_id=category_id)

    search = request.args.get("search")
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    products = query.order_by(Product.created_at.desc()).all()
    return jsonify([p.to_dict() for p in products])


@products_bp.route("/api/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product.to_dict())


@products_bp.route("/api/products", methods=["POST"])
def create_product():
    data = request.get_json()

    if not data or not data.get("name") or data.get("price") is None or not data.get("category_id"):
        return jsonify({"error": "name, price and category_id are required"}), 400

    if not db.session.get(Category, data["category_id"]):
        return jsonify({"error": "Invalid category_id"}), 400

    product = Product(
        name=data["name"],
        description=data.get("description"),
        price=data["price"],
        image_url=data.get("image_url"),
        is_available=data.get("is_available", True),
        category_id=data["category_id"],
    )
    db.session.add(product)
    db.session.commit()
    return jsonify(product.to_dict()), 201


@products_bp.route("/api/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    data = request.get_json() or {}

    product.name = data.get("name", product.name)
    product.description = data.get("description", product.description)
    product.price = data.get("price", product.price)
    product.image_url = data.get("image_url", product.image_url)
    product.is_available = data.get("is_available", product.is_available)
    product.category_id = data.get("category_id", product.category_id)

    db.session.commit()
    return jsonify(product.to_dict())


@products_bp.route("/api/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    # Order-la use aagirundha, delete pannama "unavailable" nu mark pannuvom
    if OrderItem.query.filter_by(product_id=product_id).first():
        product.is_available = False
        db.session.commit()
        return jsonify({"message": "Product is used in orders, so marked as unavailable"})

    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted"})