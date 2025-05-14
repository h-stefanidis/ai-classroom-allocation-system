from flask import Blueprint, request, jsonify
from db.db_usage import get_relationship_summary_by_run

relationship_bp = Blueprint("relationship_bp", __name__)

@relationship_bp.route("/relationship-summary", methods=["GET"])
def get_relationship_summary():
    run_number = request.args.get("run_number")

    if not run_number:
        return jsonify({"error": "run_number query parameter is required"}), 400

    try:
        df = get_relationship_summary_by_run(run_number)

        if df is None or df.empty:
            return jsonify({"message": "No data found for this run_number"}), 404

        return jsonify({
            "run_number": run_number,
            "groups": df.to_dict(orient="records")
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500