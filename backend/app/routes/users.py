from db.db_usage import login_user, register_user
from flask import Flask, request, jsonify


users_bp = Blueprint("users", __name__)

@users_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    result = login_user(data["email"], data["password"])
    if result:
        return jsonify({"message": "Login successful", "user": result}), 200
    return jsonify({"message": "Invalid credentials"}), 401


@users_bp.route("/signup", methods=["POST"])
def signup():
    data = request.json
    result = register_user(data["email"], data["password"], data["username"], data["role"])
    status_code = 200 if result["success"] else 400
    return jsonify(result), status_code
