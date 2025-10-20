import os
import csv

# ---------- CONFIG ----------
BASE_DIR = r"C:\Users\IDRESS COMPUTERS\Desktop\smart_agro_advisor\data\raw\Maize_Plantain"
OUTPUT_CSV = r"C:\Users\IDRESS COMPUTERS\Desktop\smart_agro_advisor\data\processed\maize_plantain_metadata.csv"
# ----------------------------

os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
rows = []

for crop_folder in os.listdir(BASE_DIR):
    crop_path = os.path.join(BASE_DIR, crop_folder)
    if not os.path.isdir(crop_path):
        continue

    for disease_folder in os.listdir(crop_path):
        disease_path = os.path.join(crop_path, disease_folder)
        if not os.path.isdir(disease_path):
            continue

        disease_label = disease_folder.split("___")[-1].strip()
        for img_file in os.listdir(disease_path):
            if img_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                rows.append({
                    "image_path": os.path.join(disease_path, img_file),
                    "crop": crop_folder,
                    "disease": disease_label
                })

with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["image_path", "crop", "disease"])
    writer.writeheader()
    writer.writerows(rows)

print(f"✅ Metadata saved to {OUTPUT_CSV}")
print(f"📸 Total images found: {len(rows)}")
