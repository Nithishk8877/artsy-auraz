import os
from functools import wraps
from flask import session, jsonify, redirect

# Password-a maathikonga (ippo "artsy@123")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "artsy@123")


def check_admin():
    """API routes-ku: login illana 401 error."""
    if not session.get("is_admin"):
        return jsonify({"error": "Admin login required"}), 401


def admin_required(f):
    """Page routes-ku: login illana /login-ku anuppum."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect("/login")
        return f(*args, **kwargs)
    return wrapper