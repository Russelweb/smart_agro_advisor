


---

### 📘 **README.md**

```markdown
# 🌾 Smart Agro Advisor

Smart Agro Advisor is an AI-powered system that helps farmers detect crop diseases from images and receive personalized advice based on weather data and expert rules.  
It integrates machine learning, weather APIs, and WhatsApp automation (via Twilio) to deliver instant and accessible agricultural insights.

---

## 🚀 Features

- 📸 **Crop Disease Detection** using deep learning models.  
- ☁️ **Weather Integration** via OpenWeather API.  
- 💬 **WhatsApp Chatbot Support** powered by Twilio API.  
- 🧠 **AI-Generated Recommendations** for crop management.  
- 🌍 **User-Friendly Web Interface** for uploading and analyzing crop images.

---

## 🏗️ Project Structure

```

smart_agro_advisor/
│
├── backend/
│   ├── data/
│   │   └── database/
│   ├── ml_models/         # Pretrained ML models
│   ├── models/
│   ├── routes/            # Flask Blueprints (advisory, diagnosis, weather)
│   ├── static/            # Frontend static assets
│   ├── templates/         # HTML templates
│   ├── utils/             # Helper scripts and AI logic
│   ├── app.py             # Flask backend entry point
│   └── temp.jpg           # Temporary image (auto-generated)
│
├── data/                  # Sample or external data
├── docs/                  # Documentation and references
├── env/                   # Local environment setup
├── frontend/              # (Optional) React or web UI frontend
├── models/                # Trained ML models
├── tests/                 # Unit and integration tests
├── .env                   # Environment variables (excluded from Git)
├── .gitignore
└── main.py                # Project launcher

````

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/<your-username>/smart_agro_advisor.git
cd smart_agro_advisor
````

### 2️⃣ Create a Virtual Environment

```bash
python -m venv env
source env/bin/activate      # (Mac/Linux)
env\Scripts\activate         # (Windows)
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Set Up Environment Variables

Create a `.env` file in the project root and add:

```bash
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_auth
TWILIO_WHATSAPP_NUMBER= your twilio sandbox whatsapp number
OPENWEATHER_API_KEY=your_weather_api_key
```

### 5️⃣ Run the App

```bash
python backend/app.py
```

Then open `http://127.0.0.1:5000` in your browser. or whatever port your project is running on

---

## 📡 WhatsApp Integration (Twilio)

1. Join the [Twilio Sandbox for WhatsApp](https://www.twilio.com/whatsapp).
2. Update your Twilio credentials in the `.env` file.
3. Set your webhook URL (e.g., from `ngrok`) in the Twilio Console:

   ```
   https://<your-ngrok-url>.ngrok-free.app/whatsapp
   ```

---

## 🤖 Model & AI Components

* **Disease Detection:** CNN-based image classifier trained on crop disease datasets.
* **Weather Advisory:** Fetches real-time temperature & humidity data.
* **AI Advisor:** Uses GPT-based text generation to provide adaptive farming tips.

---

## 🧪 Example Workflow

1. A user sends a crop image via WhatsApp.
2. The backend processes the image and predicts the disease.
3. Weather data for the user’s location is fetched.
4. AI generates a farming recommendation.
5. The user receives the results directly in WhatsApp.

---
## dataset downloading
maize dataset: https://www.kaggle.com/datasets/smaranjitghose/corn-or-maize-leaf-disease-dataset
plantain dataset: https://www.kaggle.com/datasets/shifatearman/bananalsd

## 🧰 Tech Stack

* **Backend:** Flask (Python)
* **ML:** TensorFlow / PyTorch
* **API:** Twilio, OpenWeather
* **Frontend:** HTML, CSS, JavaScript
* **Version Control:** Git + GitHub

---

## 🛡️ Security & Privacy

Sensitive credentials (API keys, tokens) are stored in `.env` and **never pushed to GitHub**.
The `.gitignore` file ensures no secret data or model weights are exposed.

---

## 🤝 Contributors

| Name            | Role                       |
|-----------------| -------------------------- |
| NJITA RUSSEL    | ML Engineer / Developer    |
| NJITA RUSSEL :) | Backend, Frontend, Testing |

---

## 📜 License

This project is licensed under the **MIT License** — you are free to use, modify, and distribute it with attribution.

---

## 🌟 Acknowledgments

Special thanks to:

* [Twilio](https://www.twilio.com/)
* [OpenWeather API](https://openweathermap.org/api)
* [TensorFlow](https://www.tensorflow.org/) / [PyTorch](https://pytorch.org/)
* University of Bamenda — COME Department

---

``
Thnks :)
```
