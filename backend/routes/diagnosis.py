"""
diagnosis.py
Handles routes for plant disease diagnosis using the trained CNN model.
Now supports disease-level predictions (e.g., maize_blight, plantain_sigatoka)
and provides treatment advice based on the predicted disease.
"""

import os
import json
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from backend.ml_models.disease_model import predict_disease

# -----------------------------
# CONFIG
# -----------------------------
UPLOAD_FOLDER = r"C:\Users\IDRESS COMPUTERS\Desktop\smart_agro_advisor\backend\static\uploads"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Path to local disease treatment/advisory info
DISEASE_INFO_PATH = r"C:\Users\IDRESS COMPUTERS\Desktop\smart_agro_advisor\data\disease_treatments.json"

diagnosis_bp = Blueprint("diagnosis_bp", __name__, url_prefix="/api/diagnose")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -----------------------------
# HELPERS
# -----------------------------
def allowed_file(filename):
    """Check if the uploaded file has a valid extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def load_disease_info():
    """Load disease treatment/advisory information from JSON file."""
    if os.path.exists(DISEASE_INFO_PATH):
        with open(DISEASE_INFO_PATH, 'r') as f:
            return json.load(f)
    else:
        print("⚠️ Warning: disease_treatments.json not found. Proceeding without advisory info.")
        return {}


# -----------------------------
# ROUTES
# -----------------------------
@diagnosis_bp.route("/", methods=["POST"])
def diagnose():
    """Endpoint for disease diagnosis + treatment recommendation."""
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        print(f"📥 Image received: {filepath}")

        # Run prediction
        result = predict_disease(filepath)

        # Load disease advisory info
        disease_info = load_disease_info()

        predicted_label = result.get("predicted_label")
        confidence = result.get("confidence", 0)
        treatment = disease_info.get(predicted_label, "No treatment info available for this disease yet.")

        response = {
            "status": "success",
            "filename": filename,
            "prediction": {
                "predicted_label": predicted_label,
                "confidence": round(confidence, 3),
                "probabilities": result.get("probabilities", {}),
                "treatment_advice": treatment
            }
        }

        return jsonify(response), 200

    return jsonify({"error": "Invalid file format. Allowed: PNG, JPG, JPEG"}), 400
