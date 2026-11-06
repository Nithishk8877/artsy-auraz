import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from auth import check_admin

uploads_bp = Blueprint("uploads", __name__)

ALLOWED = {"png", "jpg", "jpeg", "webp"}


@uploads_bp.route("/api/upload", methods=["POST"])
def upload_image():
    denied = check_admin()
    if denied:
        return denied

    file = request.files.get("image")
    if not file or file.filename == "":
        return jsonify({"error": "No image selected"}), 400

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED:
        return jsonify({"error": "Only png, jpg, jpeg, webp allowed"}), 400

    folder = os.path.join(current_app.root_path, "static", "uploads")
    os.makedirs(folder, exist_ok=True)

    filename = uuid.uuid4().hex + "." + ext
    file.save(os.path.join(folder, filename))
    return jsonify({"url": "/static/uploads/" + filename}), 201