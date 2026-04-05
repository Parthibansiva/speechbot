# AI Doctor - Multilingual Medical Assistant 🩺

An intelligent, multilingual AI Doctor application that can diagnose symptoms from text, voice, respiratory sounds, and medical images. It supports real-time conversation in multiple Indian languages and provides empathetic, professional medical advice.

## 🌟 Key Features

*   **Respiratory Analysis (Demo Mode)**: Analyze cough or breathing sounds to detect conditions like Asthma, COPD, and Pneumonia with realistic, randomized confidence scores (90-98%).
*   **Multilingual Support**: Support for 10+ languages including English, Tamil, Hindi, Telugu, Kannada, Malayalam, Bengali, Gujarati, Marathi, and Punjabi.
*   **Vision-AI Diagnosis**: Upload images of symptoms (e.g., skin rashes) for instant medical analysis using Llama-3.2-Vision/Llama-4-Scout.
*   **Voice-to-Voice**: Full natural conversation using Groq (Whisper) for STT and ElevenLabs for high-quality multilingual TTS.
*   **Empathetic Persona**: Mimics a professional doctor's tone, asking clarifying questions and providing concise advice.

---

## 🚀 Getting Started (Step-by-Step)

### 1. Prerequisites
- **Python 3.10+**
- **Node.js & npm** (for the Mobile App)
- **API Keys**:
    - [Groq API Key](https://console.groq.com/) (Required for LLM and Speech-to-Text)
    - [ElevenLabs API Key](https://elevenlabs.io/) (Optional, for high-quality voice)

### 2. Backend Installation
```bash
# Clone the repository
git clone <repository-url>
cd speechbot

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the `speechbot/` directory:
```env
GROQ_API_KEY=your_actual_key_here
ELEVEN_API_KEY=your_elevenlabs_key_here
```

### 4. Running the Server
```bash
# From the speechbot directory
python3 api.py
```
The server will start at `http://0.0.0.0:8000`.

---

## 🧪 Testing the API with `curl`

The API provides two main endpoints: `/predict_respiratory` and `/chat`.

### A. Respiratory Prediction (`/predict_respiratory`)
This endpoint uses "Demo Mode" logic to identify diseases based on the filename or an explicit folder name.

**Option 1: Using Filename Keywords**
If the filename contains "asthma", "copd", "pneumonia", etc., it will predict that disease.
```bash
curl -X POST http://localhost:8000/predict_respiratory \
  -F "audio=@/path/to/asthma_sample.wav"
```

**Option 2: Using the Folder Name (Recommended for Demo)**
You can upload *any* file and tell the API which folder it came from to force a specific diagnosis. This is useful when your files aren't named after the disease.
```bash
curl -X POST http://localhost:8000/predict_respiratory \
  -F "audio=@/path/to/any_file.wav" \
  -F "folder_name=Pneumonia"
```

**Response Format:**
```json
{
  "prediction": "Pneumonia",
  "confidence": 0.94,
  "all_predictions": {
    "Asthma": 0.01,
    "Pneumonia": 0.94,
    ...
  }
}
```

### B. AI Doctor Chat (`/chat`)
Send text, audio, and images to the doctor.
```bash
curl -X POST http://localhost:8000/chat \
  -F "text=I have a persistent cough" \
  -F "language=Tamil"
```

---

## 📱 Mobile App Setup (Expo)

1. **Navigate to mobile directory**: `cd mobile`
2. **Install dependencies**: `npm install`
3. **Configure API URL**: Update `BASE_URL` in `mobile/services/api.js` to your computer's local IP address (e.g., `http://192.168.1.5:8000`).
4. **Start Expo**: `npx expo start`

---

## 📂 Project Structure
- `api.py`: FastAPI backend with Demo Logic.
- `brain_of_the_doctor.py`: Logic for image analysis and LLM reasoning.
- `voice_of_the_patient.py`: Speech-to-Text via Groq Whisper.
- `voice_of_the_doctor.py`: Text-to-Speech via ElevenLabs.
- `test_audios/`: Sample audio files categorized by disease folders.

## 🛠️ Troubleshooting
- **Connection Refused**: Ensure the backend is running and you are using the correct IP/Port.
- **API Key Errors**: Double-check your `.env` file variables.
- **Audio Quality**: Ensure respiratory recordings are at least 6 seconds long for the "Extract Features" simulation to look realistic in the logs.
