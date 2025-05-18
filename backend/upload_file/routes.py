from flask import Blueprint, request, jsonify
import pandas as pd

upload_excel_bp = Blueprint('upload_excel_bp', __name__)

@upload_excel_bp.route('/upload-excel', methods=['POST'])
def upload_excel():
    print("📥 Route hit!")

    # Debugging Info
    print("📬 Headers:", dict(request.headers))
    print("📬 Form keys:", request.form)
    print("📬 Files keys:", request.files)

    file = request.files.get('file')
    cohort = request.args.get('cohort')

    print("📥 cohort =", cohort)
    print("📥 file =", file.filename if file else None)

    if not file:
        return jsonify({'error': 'No file part'}), 400
    if not cohort:
        return jsonify({'error': 'Missing cohort parameter'}), 400

    try:
        # Support both Excel and CSV
        if file.filename.endswith('.xlsx') or file.filename.endswith('.xls'):
            df = pd.read_excel(file)
        elif file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            return jsonify({'error': 'Unsupported file format'}), 400

        df['cohort'] = cohort
        print("📊 Uploaded Data:", df.head(2))

        return jsonify({
            'message': 'Upload successful',
            'cohort': cohort,
            'preview': df.head(2).to_dict(orient='records')
        })

    except Exception as e:
        print("❌ Upload error:", str(e))
        return jsonify({'error': str(e)}), 500
