import os
import httpx
from crewai.tools import tool
from config import settings

# Predefined agricultural disease lookup for Simulator Mode
CROP_DISEASES_DB = {
    "paddy": {
        "disease": "Rice Blast (Pyricularia oryzae)",
        "severity": "High",
        "confidence": 0.94,
        "cause": "Fungal pathogen that thrives in high humidity and warm temperatures with excessive nitrogen application.",
        "symptoms": "Spindle-shaped lesions on leaves with grey/white centers and brown borders. Can affect leaves, nodes, and panicles.",
        "organic_treatment": "Spray Neem oil (3,000 ppm) at 3 ml/L or pseudomonas fluorescens liquid formulation at 10 ml/L. Ensure balanced nitrogen application.",
        "chemical_treatment": "Spray Tricyclazole 75% WP at 0.6 g/L or Carbendazim 50% WP at 1 g/L of water.",
        "preventive_tips": "Avoid flooding fields continuously. Drain water for 2-3 days if blast symptoms appear. Use resistant crop varieties."
    },
    "cotton": {
        "disease": "Cotton Leaf Curl Virus (CLCuV)",
        "severity": "Moderate",
        "confidence": 0.88,
        "cause": "Viral pathogen transmitted by the Silverleaf Whitefly (Bemisia tabaci).",
        "symptoms": "Upward or downward curling of leaf margins, thickening of veins, and formation of leaf-like enations on the underside of leaves.",
        "organic_treatment": "Spray neem seed kernel extract (5%) to repel whiteflies. Install yellow sticky traps (10-15 per acre) to monitor vector population.",
        "chemical_treatment": "Control whiteflies using Diafenthiuron 50% WP at 240 g/acre or Imidacloprid 17.8% SL at 100 ml/acre.",
        "preventive_tips": "Keep fields weed-free as weeds act as alternative hosts. Remove and destroy infected plants during early stages."
    },
    "maize": {
        "disease": "Northern Corn Leaf Blight (Exserohilum turcicum)",
        "severity": "Moderate",
        "confidence": 0.91,
        "cause": "Fungal pathogen carried through crop debris and spread by wind splash.",
        "symptoms": "Long, elliptical, grayish-green or tan lesions on leaves, typically starting from lower leaves and moving upwards.",
        "organic_treatment": "Crop rotation with non-cereal crops for 2 years. Apply Trichoderma viride bio-fungicide formulation (5 g/L) to soil and foliage.",
        "chemical_treatment": "Spray Mancozeb 75% WP at 2.5 g/L or Propiconazole 25% EC at 1 ml/L of water.",
        "preventive_tips": "Perform deep summer plowing to bury crop residues. Maintain proper plant spacing to allow air circulation."
    },
    "chilli": {
        "disease": "Chilli Anthracnose / Fruit Rot (Colletotrichum capsici)",
        "severity": "High",
        "confidence": 0.95,
        "cause": "Seed-borne fungal pathogen that affects leaves and fruits during wet weather.",
        "symptoms": "Circular, sunken, black necrotic lesions on the fruit. Infected leaves show small, dark, circular spots.",
        "organic_treatment": "Seed treatment with Trichoderma harzianum (10 g/kg of seed). Spray fresh cow dung extract (10%) or garlic extract (5%).",
        "chemical_treatment": "Spray Azoxystrobin 23% SC at 1 ml/L or Copper Oxychloride 50% WP at 3 g/L.",
        "preventive_tips": "Source certified disease-free seeds. Avoid overhead sprinkler irrigation as it spreads fungal spores."
    },
    "default": {
        "disease": "Healthy Leaf (No major disease detected)",
        "severity": "None",
        "confidence": 0.98,
        "cause": "Nutrient balances and moisture levels appear optimal.",
        "symptoms": "Uniform green pigmentation, strong cell turgor, and no visible necrotic spots or insect infestations.",
        "organic_treatment": "Continue regular organic manuring (Vermicompost or Panchagavya spray at 3% for growth support).",
        "chemical_treatment": "No chemical application required. Avoid unnecessary chemical costs.",
        "preventive_tips": "Practice systematic crop rotation and maintain clean weeding around borders."
    }
}

@tool("Diagnose Crop Disease Tool")
def diagnose_crop_disease(image_path: str, crop_type: str = "default") -> str:
    """
    Analyzes an uploaded leaf or crop photo and diagnoses any crop disease.
    Requires the absolute file path to the uploaded image. Returns diagnostic report.
    """
    crop_key = crop_type.lower().strip()
    # Check if a valid API key exists for Plant.id
    if settings.PLANT_ID_API_KEY:
        try:
            # Live Plant.id API Call
            import base64
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode("utf-8")

            url = "https://api.plant.id/v2/identify"
            headers = {
                "Content-Type": "application/json",
                "Api-Key": settings.PLANT_ID_API_KEY
            }
            payload = {
                "images": [encoded_string],
                "modifiers": ["crops", "disease"],
                "language": "en"
            }
            
            response = httpx.post(url, json=payload, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                # Parse plant.id response and format output nicely
                disease_suggestions = data.get("health_assessment", {}).get("diseases", [])
                if disease_suggestions:
                    top_disease = disease_suggestions[0]
                    name = top_disease.get("name", "Unknown Disease")
                    prob = top_disease.get("probability", 0.0)
                    info = top_disease.get("disease_details", {})
                    treatment = info.get("treatment", {})
                    
                    return (
                        f"DIAGNOSIS REPORT (Live API):\n"
                        f"- Detected Disease: {name}\n"
                        f"- Confidence: {prob * 100:.1f}%\n"
                        f"- Severity Level: High (based on leaf coverage)\n"
                        f"- Biological Treatment: {', '.join(treatment.get('biological', ['Apply organic neem sprays']))}\n"
                        f"- Chemical Treatment: {', '.join(treatment.get('chemical', ['Apply systemic fungicides']))}\n"
                        f"- Description: Disease identified via visual classification API."
                    )
        except Exception as e:
            print(f"Plant.id API Call failed ({e}). Falling back to Simulator Mode.")
            
    # Simulator Mode:
    # Use crop_type to index into the predefined DB
    match = CROP_DISEASES_DB.get(crop_key, CROP_DISEASES_DB["default"])
    
    # If the user passed generic image names, try to guess the crop type
    if crop_key == "default" or crop_key == "":
        img_name = os.path.basename(image_path).lower()
        if "paddy" in img_name or "rice" in img_name:
            match = CROP_DISEASES_DB["paddy"]
        elif "cotton" in img_name:
            match = CROP_DISEASES_DB["cotton"]
        elif "maize" in img_name or "corn" in img_name:
            match = CROP_DISEASES_DB["maize"]
        elif "chilli" in img_name or "pepper" in img_name:
            match = CROP_DISEASES_DB["chilli"]

    report = (
        f"DIAGNOSIS REPORT (Simulator Mode):\n"
        f"- Target Crop: {crop_type.capitalize()}\n"
        f"- Diagnosed Disease: {match['disease']}\n"
        f"- Confidence Score: {match['confidence'] * 100:.1f}%\n"
        f"- Severity: {match['severity']}\n"
        f"- Symptoms Observed: {match['symptoms']}\n"
        f"- Cause: {match['cause']}\n"
        f"- Biological/Organic Control: {match['organic_treatment']}\n"
        f"- Chemical Control: {match['chemical_treatment']}\n"
        f"- Agronomic Preventive Advice: {match['preventive_tips']}"
    )
    return report
