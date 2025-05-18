
from flask import Blueprint, request, jsonify, session
from functools import wraps
from backend.classforge_project.data_analysis.sna_data_analysis import *
from backend.classforge_project.data_analysis.sna_relationship_graph import *
from backend.classforge_project.data_analysis.statistical_analysis import final_calculate_with_normalized_scores
from db.db_manager import get_db


# Create a Blueprint for authentication routess
stats_bp = Blueprint('stats', __name__)

@stats_bp.route("/psychometrics-stats-normalized", methods=["GET"])
def final_calculate_with_normalized_score():
    db = get_db()
    run_number = request.args.get("run_number",None)
    cohort = request.args.get("cohort", "2025")

    try:
        result = final_calculate_with_normalized_scores(db, run_number, cohort)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
