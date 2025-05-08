
from flask import Blueprint, request, jsonify, session
from create_app import db, bcrypt
from app.models.db_models import *
from functools import wraps
from classforge_project.data_analysis.sna_data_analysis import *
from classforge_project.data_analysis.sna_relationship_graph import *


# Create a Blueprint for authentication routess
student_rel_bp = Blueprint('student_rel_analy', __name__)



"""
Example response:
Nodes: Number of unique students involved in each network.

Edges: Number of directed connections (e.g., "Student A selected B as a friend").

Top In-Degree: Students most frequently nominated by others (popularity/influence).

Top Out-Degree: Students who nominated many others (active or seeking).

Top Betweenness: Students acting as bridges between groups (social connectors).
{
  "friend": {
    "num_nodes": 675,
    "num_edges": 4739,
    "top_in_degree": [
      { "node": 32407, "value": 26 },
      { "node": 32405, "value": 23 }
    ],
    "top_out_degree": [
      { "node": 32409, "value": 35 },
      { "node": 32534, "value": 23 }
    ],
    "top_betweenness": [
      { "node": 1182, "value": 0.01478 },
      { "node": 32409, "value": 0.01418 }
    ]
  },
  "influence": {
    "num_nodes": 673,
    "num_edges": 1722,
    ...
  }
}

"""
@student_rel_bp.route("/relationship_data", methods=["GET"])
def sna_summary():
    try:
        result = analyze_networks_from_db()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@student_rel_bp.route("/friend-network-graph", methods=["GET"])
def friend_network_route():
    try:
        return get_friend_network_graph()
    except Exception as e:
        return {"error": str(e)}, 500

