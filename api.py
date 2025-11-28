import os
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import base64
from typing import Optional
from groq import Groq

# Load env vars
load_dotenv()

# Import core functions
from brain_of_the_doctor import encode_image, analyze_image_with_query
from voice_of_the_patient import transcribe_with_groq
from voice_of_the_doctor import text_to_speech_with_elevenlabs

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SYSTEM_PROMPT = """
You are a professional, empathetic doctor. Your goal is to diagnose the patient through a natural conversation.

1. **Start of Conversation**: If the user greets you (e.g., "Hello"), respond politely: "Hello, I am your AI Doctor. How can I help you today? Are you feeling unwell?"
2. **Gathering Information**: Do not jump to a diagnosis immediately. Ask clarifying questions step-by-step to understand the symptoms better (e.g., "How long have you had this?", "Is the pain sharp or dull?", "Do you have any other symptoms?").
3. **Diagnosis**: Only provide a diagnosis and remedies after you have gathered sufficient information or if the user provides an image.
4. **Image Analysis**: If an image is provided, analyze it medically. Say "Based on the image..." instead of "In the image I see...".
5. **Response Style**:
   - Be concise (max 3 sentences).
   - Speak naturally as a human doctor.
   - Do not use Markdown or special formatting.
   - Do not mention you are an AI unless asked.
"""

@app.post("/chat")
@app.post("/chat")
async def chat(
    audio: Optional[UploadFile] = File(None),
    image: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
    history: Optional[str] = Form(None),
    language: Optional[str] = Form("English")
):
    try:
        transcription = ""
        
        # Handle Audio Input
        if audio:
            audio_path = f"temp_{audio.filename}"
            with open(audio_path, "wb") as buffer:
                shutil.copyfileobj(audio.file, buffer)

            # Transcribe audio
            transcription = transcribe_with_groq(
                stt_model="whisper-large-v3",
                audio_filepath=audio_path,
                GROQ_API_KEY=os.environ.get("GROQ_API_KEY")
            )
            
            # Cleanup audio input file
            if os.path.exists(audio_path):
                os.remove(audio_path)
        
        # Use provided text if no audio or as supplement
        if text:
            transcription = text if not transcription else f"{transcription} {text}"

        if not transcription and not image:
             return JSONResponse(content={"error": "No input provided"}, status_code=400)

        # Prepare Messages
        # Update System Prompt based on language
        current_system_prompt = SYSTEM_PROMPT
        if language and language.lower() != "english":
            current_system_prompt += f"\n\nIMPORTANT: The user prefers to speak in {language}. Please provide your response in {language}."

        messages = [{"role": "system", "content": current_system_prompt}]
        
        # Add History
        if history:
            try:
                import json
                history_list = json.loads(history)
                for msg in history_list:
                    # Filter out internal keys if any, ensure strict role/content structure
                    if msg.get("role") in ["user", "assistant"]:
                        messages.append({
                            "role": msg["role"],
                            "content": msg["content"]
                        })
            except Exception as e:
                print(f"Error parsing history: {e}")

        # Prepare Current User Message
        user_content = []
        if transcription:
            user_content.append({"type": "text", "text": transcription})
        
        if image:
            # Sanitize filename to handle potential issues with blob URLs or special chars
            safe_filename = "".join(x for x in image.filename if x.isalnum() or x in "._-")
            image_path = f"temp_{safe_filename}"
            with open(image_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
            
            encoded_image = encode_image(image_path)
            user_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}
            })
            
            if os.path.exists(image_path):
                os.remove(image_path)

        messages.append({"role": "user", "content": user_content})

        # Select Model
        if image:
            model = "meta-llama/llama-4-scout-17b-16e-instruct"
        else:
            model = "llama-3.3-70b-versatile" 
        
        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        chat_completion = client.chat.completions.create(
            messages=messages,
            model=model,
            temperature=0.7,
            max_tokens=500
        )
        
        doctor_response = chat_completion.choices[0].message.content

        # Text to Speech
        output_audio_path = "response.mp3"
        text_to_speech_with_elevenlabs(
            input_text=doctor_response,
            output_filepath=output_audio_path,
            language=language
        )

        # Encode audio to base64
        audio_base64 = None
        if os.path.exists(output_audio_path):
            with open(output_audio_path, "rb") as audio_file:
                audio_base64 = base64.b64encode(audio_file.read()).decode('utf-8')
            os.remove(output_audio_path)

        return JSONResponse(content={
            "transcription": transcription,
            "response": doctor_response,
            "audio_base64": audio_base64
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
