from flask import Blueprint, jsonify
from db.db_usage import get_all_allocation_run_numbers

allocation_bp = Blueprint("allocation_bp", __name__)

@allocation_bp.route("/allocation-runs", methods=["GET"])
def fetch_all_run_numbers():
    try:
        df = get_all_allocation_run_numbers()
        return jsonify({
            "run_numbers": df["run_number"].tolist()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500