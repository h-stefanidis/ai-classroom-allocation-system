from flask import Blueprint, jsonify
from db.db_manager import get_visualization_data

nodes_bp = Blueprint("nodes", __name__)

@nodes_bp.route("/nodes", methods=["GET"])
def get_node_data():
    return jsonify(get_visualization_data())