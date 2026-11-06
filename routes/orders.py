from datetime import date, timedelta
from flask import Blueprint, request, jsonify
from models import db, Product, Customer, Order, OrderItem
from auth import check_admin

orders_bp = Blueprint("orders", __name__)


@orders_bp.before_request
def require_admin_except_create():
    # Order place panradhu (POST) public. Matha ellam admin mattum.
    if request.method == "POST":
        return None
    return check_admin()

VALID_STATUSES = [
    "Pending Payment",
    "Paid",
    "In Making",
    "Shipped",
    "Delivered",
    "Cancelled",
]
MAKING_DAYS = 10  # shop rule: making days 7-10


@orders_bp.route("/api/orders", methods=["POST"])
def create_order():
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    cust_data = data.get("customer") or {}
    items_data = data.get("items") or []

    if not cust_data.get("name") or not cust_data.get("phone"):
        return jsonify({"error": "customer name and phone are required"}), 400
    if not items_data:
        return jsonify({"error": "At least one item is required"}), 400

    # Same phone number irundha, already irukkura customer-a use pannuvom
    customer = Customer.query.filter_by(phone=cust_data["phone"]).first()
    if not customer:
        customer = Customer(
            name=cust_data["name"],
            phone=cust_data["phone"],
            email=cust_data.get("email"),
            address=cust_data.get("address"),
        )
        db.session.add(customer)
        db.session.flush()

    order = Order(
        customer_id=customer.id,
        delivery_address=data.get("delivery_address") or cust_data.get("address"),
        expected_delivery=date.today() + timedelta(days=MAKING_DAYS),
    )

    total = 0
    for item in items_data:
        product = db.session.get(Product, item.get("product_id"))
        if not product or not product.is_available:
            db.session.rollback()
            return jsonify({"error": f"Product {item.get('product_id')} not available"}), 400

        quantity = item.get("quantity", 1)
        if not isinstance(quantity, int) or quantity < 1:
            db.session.rollback()
            return jsonify({"error": "quantity must be 1 or more"}), 400

        total += product.price * quantity
        order.items.append(
            OrderItem(
                product_id=product.id,
                quantity=quantity,
                price=product.price,
                customization_note=item.get("customization_note"),
            )
        )

    order.total_amount = total
    db.session.add(order)
    db.session.commit()
    return jsonify(order.to_dict()), 201


@orders_bp.route("/api/orders", methods=["GET"])
def get_orders():
    query = Order.query

    status = request.args.get("status")
    if status:
        query = query.filter_by(status=status)

    orders = query.order_by(Order.order_date.desc()).all()
    return jsonify([o.to_dict() for o in orders])


@orders_bp.route("/api/orders/<int:order_id>", methods=["GET"])
def get_order(order_id):
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    return jsonify(order.to_dict())


@orders_bp.route("/api/orders/<int:order_id>/payment", methods=["PUT"])
def mark_paid(order_id):
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    data = request.get_json() or {}
    order.payment_status = "Paid"
    order.upi_reference = data.get("upi_reference")
    if order.status == "Pending Payment":
        order.status = "Paid"

    db.session.commit()
    return jsonify(order.to_dict())


@orders_bp.route("/api/orders/<int:order_id>/status", methods=["PUT"])
def update_status(order_id):
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    data = request.get_json() or {}
    new_status = data.get("status")
    if new_status not in VALID_STATUSES:
        return jsonify({"error": f"status must be one of {VALID_STATUSES}"}), 400

    order.status = new_status
    db.session.commit()
    return jsonify(order.to_dict())