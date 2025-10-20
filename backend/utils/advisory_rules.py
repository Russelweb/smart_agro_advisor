"""
advisory_rules.py
Contains AI-driven rule-based logic for actionable recommendations
based on crop, disease, and weather data.
"""

def get_disease_advice(crop, disease_name, weather_summary):
    """
    Generate practical recommendations for the farmer.
    """
    advice = []

    # --- Maize Diseases ---
    if crop.lower() == "maize":
        if "blight" in disease_name.lower():
            advice.append("Spray copper-based fungicides during dry conditions.")
            advice.append("Remove infected leaves to prevent spread.")
        elif "rust" in disease_name.lower():
            advice.append("Use resistant maize varieties if available.")
            advice.append("Apply Mancozeb or Propiconazole at early infection.")
        elif "streak" in disease_name.lower():
            advice.append("Control insect vectors (aphids) with appropriate insecticides.")
            advice.append("Avoid planting new maize near infected fields.")

    # --- Plantain Diseases ---
    elif crop.lower() == "plantain":
        if "black_sigatoka" in disease_name.lower():
            advice.append("Prune affected leaves and destroy them.")
            advice.append("Use systemic fungicides like Propiconazole.")
        elif "banana_bunchy_top" in disease_name.lower():
            advice.append("Remove and burn infected suckers immediately.")
            advice.append("Control aphids to limit transmission.")

    # --- Weather-based Enhancements ---
    if "rain" in weather_summary.lower():
        advice.append("Avoid applying pesticides or fertilizers before rainfall.")
    elif "dry" in weather_summary.lower():
        advice.append("Irrigate if soil moisture is low and no rain expected soon.")
    else:
        advice.append("Monitor soil moisture and weather regularly.")

    if not advice:
        advice.append("No specific recommendation — monitor crop health regularly.")

    return advice
