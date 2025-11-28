# AI Doctor - Multilingual Medical Assistant

An intelligent, multilingual AI Doctor application that can diagnose symptoms from text, voice, and medical images. It supports real-time conversation in multiple Indian languages and provides empathetic, professional medical advice.

## Features

*   **Multilingual Support**: Speak or type in English, Tamil, Hindi, Telugu, Kannada, Malayalam, Bengali, Gujarati, Marathi, or Punjabi. The AI responds in the selected language.
*   **Voice Interaction**: Full voice-to-voice conversation capability. Speak your symptoms, and the AI Doctor speaks back.
*   **Image Analysis**: Upload medical images (e.g., skin rashes, X-rays) for instant analysis and diagnosis using advanced vision models.
*   **Empathetic Persona**: Designed to act like a professional human doctor, asking clarifying questions before providing a diagnosis.
*   **Cross-Platform**: Runs as a mobile app (iOS/Android via Expo) and a web app.

## Tech Stack

*   **Backend**: Python, FastAPI
*   **Frontend**: React Native (Expo)
*   **AI Models**:
    *   **LLM**: `llama-3.3-70b-versatile` (Text) / `meta-llama/llama-4-scout-17b-16e-instruct` (Vision) via Groq
    *   **STT (Speech-to-Text)**: `whisper-large-v3` via Groq
    *   **TTS (Text-to-Speech)**: ElevenLabs (Multilingual) / Google TTS (Fallback)
*   **Translation**: `deep-translator`

## Prerequisites

*   Python 3.8+
*   Node.js & npm
*   Groq API Key
*   ElevenLabs API Key (Optional, for high-quality voice)

## Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd speechbot
    ```

2.  **Backend Setup**:
    *   Create a virtual environment:
        ```bash
        python -m venv venv
        source venv/bin/activate  # On Windows: venv\Scripts\activate
        ```
    *   Install dependencies:
        ```bash
        pip install -r requirements.txt
        ```
    *   Create a `.env` file in the root directory:
        ```env
        GROQ_API_KEY=your_groq_api_key
        ELEVENLABS_API_KEY=your_elevenlabs_api_key
        ```

3.  **Mobile App Setup**:
    *   Navigate to the mobile directory:
        ```bash
        cd mobile
        ```
    *   Install dependencies:
        ```bash
        npm install
        ```

## Running the Application

1.  **Start the Backend**:
    From the root `speechbot` directory:
    ```bash
    source venv/bin/activate
    uvicorn api:app --reload --host 0.0.0.0 --port 8000
    ```
    The backend will run at `http://localhost:8000`.

2.  **Start the Mobile App**:
    From the `mobile` directory:
    ```bash
    npx expo start
    ```
    *   **Web**: Press `w` to run in the browser.
    *   **Mobile**: Scan the QR code with the Expo Go app on your Android/iOS device.
    *   **Emulator**: Press `a` for Android or `i` for iOS (requires setup).

## How to Use

1.  **Select Language**: Tap the language button in the top right corner to choose your preferred language (e.g., Tamil, Hindi).
2.  **Voice Input**: Tap the microphone icon and speak your symptoms. Tap stop to send.
3.  **Text Input**: Type your symptoms in the text box and hit send.
4.  **Image Input**: Tap the image icon to upload a photo of a visible symptom (e.g., a rash).
5.  **Diagnosis**: The AI Doctor will analyze your input and respond with voice and text in your chosen language.

## Troubleshooting

*   **Network Error**: Ensure your mobile device and computer are on the same Wi-Fi network. Update `mobile/services/api.js` with your computer's local IP address if not using localhost.
*   **Audio/Image Issues**: Grant necessary permissions (Microphone, Camera) to the Expo Go app.
