# VoiceBot UI with Gradio
import os
from dotenv import load_dotenv

# IMPORTANT: Load environment variables BEFORE importing other modules
load_dotenv()

import tempfile
import soundfile as sf
import gradio as gr
import numpy as np
from tempfile import NamedTemporaryFile

# Import functions from other modules AFTER load_dotenv()
from brain_of_the_doctor import encode_image, analyze_image_with_query
from voice_of_the_patient import transcribe_with_groq
from voice_of_the_doctor import text_to_speech_with_elevenlabs

# Debug: Check if API keys are loaded
print("=" * 50)
print("API Keys Status:")
print(f"GROQ_API_KEY: {'✓ Loaded' if os.environ.get('GROQ_API_KEY') else '✗ Not Found'}")
eleven_key = os.environ.get('ELEVEN_API_KEY') or os.environ.get('ELEVENLABS_API_KEY')
print(f"ElevenLabs API Key: {'✓ Loaded' if eleven_key else '✗ Not Found'}")
if eleven_key:
    print(f"  (Key length: {len(eleven_key)} characters)")
print("=" * 50)
print()

# ---------------- SYSTEM PROMPT ----------------
system_prompt = """
You have to act as a professional doctor, I know you are not but this is for learning purpose.
What's in this image? Do you find anything wrong with it medically?
If you make a differential, suggest some remedies for them. 
Do not add any numbers or special characters in your response.
Your response should be in one long paragraph. 
Also, always answer as if you are answering to a real person.
Do not say 'In the image I see' but say 'With what I see, I think you have ...'
Do not respond as an AI model in markdown — your answer should mimic that of an actual doctor, not an AI bot.
Keep your answer concise (max 3 important sentences). 
No preamble — start your answer right away please.
"""

# ---------------- MAIN FUNCTION ----------------
def process_inputs(audio_data, image_filepath):
    if audio_data is None:
        return "No audio detected.", "Please record your voice again.", None

    try:
        # Debug: Check what we received
        print(f"Audio data type: {type(audio_data)}")
        print(f"Audio data structure: {audio_data if not isinstance(audio_data, tuple) else (type(audio_data[0]), type(audio_data[1]) if len(audio_data) > 1 else None)}")
        
        # Gradio sends (sample_rate, numpy_array) when type="numpy"
        sample_rate, audio_np = audio_data
        
        print(f"Sample rate: {sample_rate}, Audio shape: {audio_np.shape if hasattr(audio_np, 'shape') else 'no shape'}")

        # Ensure audio_np is a numpy array
        if not isinstance(audio_np, np.ndarray):
            return "Invalid audio format.", "Audio data is not in the correct format.", None

        # Save audio to temporary file (soundfile handles mono/stereo automatically)
        with NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio:
            sf.write(tmp_audio.name, audio_np, sample_rate)
            audio_filepath = tmp_audio.name

        # Transcribe with Groq Whisper
        speech_to_text_output = transcribe_with_groq(
            GROQ_API_KEY=os.environ.get("GROQ_API_KEY"),
            audio_filepath=audio_filepath,
            stt_model="whisper-large-v3"
        )

        # Handle image + text query
        if image_filepath:
            doctor_response = analyze_image_with_query(
                query=system_prompt + speech_to_text_output,
                encoded_image=encode_image(image_filepath),
                model="meta-llama/llama-4-scout-17b-16e-instruct"
            )
        else:
            doctor_response = "No image provided for me to analyze."

        # Convert doctor's text to voice
        voice_of_doctor = text_to_speech_with_elevenlabs(
            input_text=doctor_response,
            output_filepath="final.mp3",
            translate=True  # Translate English to Tamil
        )
        
        # Check if TTS was successful
        if voice_of_doctor is None:
            print("Warning: Text-to-speech conversion failed. Returning text response only.")

        # Clean up temporary audio file
        try:
            os.unlink(audio_filepath)
        except Exception as cleanup_error:
            print(f"Cleanup error: {cleanup_error}")

        return speech_to_text_output, doctor_response, voice_of_doctor

    except Exception as e:
        print("Error:", e)
        import traceback
        traceback.print_exc()
        return "Audio processing failed.", str(e), None


# ---------------- GRADIO INTERFACE ----------------
iface = gr.Interface(
    fn=process_inputs,
    inputs=[
        gr.Audio(sources=["microphone"], type="numpy", label="🎙️ Speak Your Symptoms"),
        gr.Image(type="filepath", label="Upload or Capture an Image")
    ],
    outputs=[
        gr.Textbox(label="Speech to Text (Patient's Voice)"),
        gr.Textbox(label="Doctor's Response"),
        gr.Audio(label="Doctor's Voice Reply")
    ],
    title="🩺 AI Doctor with Vision and Voice",
    description="Speak your symptoms and upload an image — the AI Doctor will respond with a diagnosis and speak back to you."
)

# Run app
if __name__ == "__main__":
    iface.launch(share=True, debug=True)
