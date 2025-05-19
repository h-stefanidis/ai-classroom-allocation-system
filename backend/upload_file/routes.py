from flask import Blueprint, request, jsonify
import os
import pandas as pd

upload_bp = Blueprint('upload', __name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@upload_bp.route('/upload-excel', methods=['POST'])
def upload_excel():
    # ✅ Get cohort from form
    cohort = request.form.get("cohort")
    if not cohort:
        return jsonify({"error": "Missing cohort value"}), 400

    try:
        cohort = int(cohort)
    except ValueError:
        return jsonify({"error": "Invalid cohort value, must be an integer"}), 400

    # ✅ Check file part
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if not file.filename.endswith(('.xls', '.xlsx')):
        return jsonify({"error": "Invalid file type. Please upload an Excel file."}), 400

    try:
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        # ✅ Read Excel safely
        try:
            df = pd.read_excel(filepath)
        except Exception as e:
            return jsonify({"error": f"Failed to read Excel file: {str(e)}"}), 400

        # ✅ Add cohort column
        df["Cohort"] = cohort

        return jsonify({
            "message": "File uploaded successfully",
            "rows": len(df),
            "columns": list(df.columns),
            "cohort": cohort
        }), 200

    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500
