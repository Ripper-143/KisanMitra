# KisanMitra (किसानमित्र / కిసాన్ మిత్ర)
### AI Farm Advisory Multi-Agent System — Hackathon 2.0

KisanMitra is a full-stack, multi-agent farm advisory platform built with **FastAPI**, **React (Vite) + TailwindCSS**, and **CrewAI** orchestration. It is designed to assist small and marginal farmers (specifically in Andhra Pradesh and Telangana) by delivering real-time weather advisories, crop disease classification, market price insights, government subsidy matching, and instant alert dispatches.

---

## Key Features & 5-Agent Architecture

Unlike a standard single-prompt LLM wrapper, KisanMitra coordinates **five specialized agents** performing concrete tool operations:

1. **Crop Health Agent**: Diagnoses plant leaf diseases using a vision-classification tool (HuggingFace Plant Disease classification or Plant.id API) and outputs organic & chemical treatments.
2. **Market Price Agent**: Queries live market (mandi) rate feeds from data.gov.in Agmarknet API and recommends the best mandi and selling plan.
3. **Weather Advisory Agent**: Calls OpenWeatherMap API for live micro-climate forecasts, compiling daily agricultural advisories (spraying suitability index, irrigation volumes, sowing schedules).
4. **Scheme Matcher Agent**: Employs **RAG (Retrieval-Augmented Generation)** over government policy documents indexed in a local **ChromaDB** database (includes PM-Kisan, PMFBY, Rythu Bharosa, Rythu Bandhu guidelines) to match eligible subsidies.
5. **Alert & Notification Agent**: Sends SMS alerts to the farmer via the **Twilio SMS API** and logs dispatch histories into a relational database.

> **Note on Simulator Mode**: To support rapid testing and offline evaluations, the system runs in a **Dual-Mode**. If external API credentials are left blank in `.env`, the tools fall back to realistic local simulation databases (incorporating regional Guntur, Warangal, Khammam mandis, and Paddy, Cotton, Chilli crop models).

---

## Regional Multilingual Support
KisanMitra incorporates a real-time toggle supporting:
- 🇬🇧 **English (EN)**
- 🇮🇳 **Telugu (TE / తెలుగు)**
- 🇮🇳 **Hindi (HI / हिन्दी)**

This allows farmers to review advisor remarks, navigation prompts, and inputs in their local language.

---

## Project Structure
```
kisanmitra/
├── backend/
│   ├── agents/          # CrewAI agent & task orchestration (crew.py)
│   ├── tools/           # Concrete tools (crop, price, weather, rag, sms)
│   ├── routes/          # FastAPI routers (auth, crop, market, weather, schemes, alerts)
│   ├── models/          # Database ORM models (Farmer, LandProfile, AlertLog)
│   ├── rag/             # ChromaDB vector client and document ingestion
│   │   └── schemes/     # Guidelines text files for PM-Kisan, PMFBY, etc.
│   ├── main.py          # Entrypoint & static serving
│   ├── config.py        # Settings configuration (Pydantic Settings)
│   ├── auth.py          # JWT authentication context
│   └── requirements.txt # Python dependency configurations
│
├── frontend/
│   ├── src/
│   │   ├── components/  # Navbars, layout panels
│   │   ├── pages/       # Login, Signup, Dashboard, CropUpload, MarketPrices, Schemes, Alerts
│   │   ├── translations.js # Localization strings dict (EN, TE, HI)
│   │   ├── App.jsx      # Navigation routing & global auth
│   │   └── index.css    # Tailwind layer styling & custom scrollbars
│   ├── tailwind.config.js
│   └── package.json
└── README.md
```

---

## Installation & Setup

### 1. Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure `.env` values (set LLM and API keys as desired; leave empty to run in Simulator mode).
5. Run the server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

### 2. Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd ../frontend
   ```
2. Install node packages:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
4. Access the web interface at `http://localhost:5173`.

---

## Running Verification Tests
To run backend unit test suites checking JWT security and RAG queries:
```bash
cd backend
python -m unittest test_backend.py
```
