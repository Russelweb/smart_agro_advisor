"""
disease_model.py
Handles loading the trained CNN (MobileNetV2) and performing inference
for maize and plantain leaf diseases with disease-level classification.
"""

import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import joblib

# -----------------------------
# CONFIG
# -----------------------------
MODEL_PATH = r"C:\Users\IDRESS COMPUTERS\Desktop\smart_agro_advisor\models\disease_model.h5"
ENCODER_PATH = r"C:\Users\IDRESS COMPUTERS\Desktop\smart_agro_advisor\models\label_encoder.pkl"
IMG_SIZE = (224, 224)

# -----------------------------
# LOAD MODEL + LABEL ENCODER
# -----------------------------
print("🔄 Loading disease classification model and label encoder...")

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"❌ Model file not found at: {MODEL_PATH}")

if not os.path.exists(ENCODER_PATH):
    raise FileNotFoundError(f"❌ Label encoder not found at: {ENCODER_PATH}")

model = tf.keras.models.load_model(MODEL_PATH)
label_map = joblib.load(ENCODER_PATH)
index_to_label = {v: k for k, v in label_map.items()}

print("✅ Model and label encoder loaded successfully.")
print("📚 Classes detected:", index_to_label)

# -----------------------------
# IMAGE PREPROCESSING
# -----------------------------
def preprocess_image(img_path):
    """Load and preprocess an image for model prediction."""
    if not os.path.exists(img_path):
        raise FileNotFoundError(f"Image file not found: {img_path}")

    img = image.load_img(img_path, target_size=IMG_SIZE)
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0
    return img_array


# -----------------------------
# PREDICTION FUNCTION
# -----------------------------
def predict_disease(img_path):
    """
    Predict crop disease given an image path.
    Returns a JSON-serializable dictionary with:
      - predicted_label
      - confidence
      - probabilities (dict)
    """
    try:
        # Preprocess input image
        img_array = preprocess_image(img_path)

        # Run inference
        preds = model.predict(img_array)
        pred_index = int(np.argmax(preds[0]))
        confidence = float(preds[0][pred_index])
        predicted_label = index_to_label[pred_index]

        # Convert probabilities to readable mapping
        probabilities = {
            index_to_label[i]: float(round(p, 4)) for i, p in enumerate(preds[0])
        }

        print(f"🧠 Prediction completed:")
        print(f"   - Label: {predicted_label}")
        print(f"   - Confidence: {confidence * 100:.2f}%")
        print(f"   - All probabilities: {probabilities}")

        # Return structured result
        return {
            "predicted_label": predicted_label,
            "confidence": confidence,
            "probabilities": probabilities
        }

    except Exception as e:
        print(f"❌ Error during prediction: {str(e)}")
        return {"error": str(e)}


# -----------------------------
# TEST (Standalone Execution)
# -----------------------------
if __name__ == "__main__":
    # Example test
    test_image = r"C:\Users\IDRESS COMPUTERS\Desktop\smart_agro_advisor\data\raw\Maize_Plantain\Plantain___pestalotiopsis\4_aug.jpeg"
    if os.path.exists(test_image):
        result = predict_disease(test_image)
        print("\n🔍 Test Prediction Result:")
        print(result)
    else:
        print("⚠️ Test image not found — update test path to a real file.")
