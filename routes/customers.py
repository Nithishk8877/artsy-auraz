from flask import Blueprint, jsonify
from models import db, Customer
from auth import check_admin

customers_bp = Blueprint("customers", __name__)


@customers_bp.before_request
def require_admin():
    # Customer details ellam admin mattum
    return check_admin()


@customers_bp.route("/api/customers", methods=["GET"])
def get_customers():
    customers = Customer.query.all()
    return jsonify([c.to_dict() for c in customers])


@customers_bp.route("/api/customers/<int:customer_id>", methods=["GET"])
def get_customer(customer_id):
    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    return jsonify(customer.to_dict())