from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    products = db.relationship("Product", backref="category", lazy=True)

    def to_dict(self):
        return {"id": self.id, "name": self.name}


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(300))
    is_available = db.Column(db.Boolean, default=True)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "image_url": self.image_url,
            "is_available": self.is_available,
            "category_id": self.category_id,
            "category": self.category.name if self.category else None,
        }


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120))
    address = db.Column(db.Text)
    orders = db.relationship("Order", backref="customer", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "address": self.address,
        }


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False)
    status = db.Column(db.String(30), default="Pending Payment")
    payment_status = db.Column(db.String(20), default="Unpaid")
    upi_reference = db.Column(db.String(100))
    delivery_address = db.Column(db.Text)
    total_amount = db.Column(db.Float, default=0)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    expected_delivery = db.Column(db.Date)
    items = db.relationship("OrderItem", backref="order", cascade="all, delete-orphan", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "customer": self.customer.to_dict() if self.customer else None,
            "status": self.status,
            "payment_status": self.payment_status,
            "upi_reference": self.upi_reference,
            "delivery_address": self.delivery_address,
            "total_amount": self.total_amount,
            "order_date": self.order_date.isoformat() if self.order_date else None,
            "expected_delivery": self.expected_delivery.isoformat() if self.expected_delivery else None,
            "items": [item.to_dict() for item in self.items],
        }


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    price = db.Column(db.Float, nullable=False)
    customization_note = db.Column(db.Text)
    product = db.relationship("Product")

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "product_name": self.product.name if self.product else None,
            "quantity": self.quantity,
            "price": self.price,
            "customization_note": self.customization_note,
        }