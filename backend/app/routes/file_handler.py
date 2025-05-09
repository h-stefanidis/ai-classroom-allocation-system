from flask import Flask, request, jsonify,Blueprint
from werkzeug.utils import secure_filename
from classforge_project.file_upload.file_handle import *
import os
file_handler_bp = Blueprint("file_handler_bp", __name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {"xlsx"}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@file_handler_bp.route("/upload-excel", methods=["POST"])
def upload_excel():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    cohort = request.form.get("cohort")

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"}), 400

    if not cohort:
        return jsonify({"error": "Missing cohort value"}), 400

    try:
        # Use a safe upload directory and ensure it's created
        upload_dir = os.path.join(os.getcwd(), "upload_file")
        os.makedirs(upload_dir, exist_ok=True)

        # Secure the filename and define full path
        filename = secure_filename(file.filename)
        temp_path = os.path.join(upload_dir, filename)

        # Save file safely
        file.save(temp_path)

        # Now pass it to your handler (which must use 'with pd.ExcelFile'!)
        insert_excel_data_to_db(temp_path, cohort)

        return jsonify({"message": "File processed and data inserted"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        # Ensure file is deleted if it exists
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except PermissionError:
            pass  # Skip if the file is still in use