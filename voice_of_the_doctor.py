import os
import elevenlabs
from elevenlabs.client import ElevenLabs
import subprocess
import platform
from gtts import gTTS
from deep_translator import GoogleTranslator

# Check for API key - try both common environment variable names
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY") or os.environ.get("ELEVEN_API_KEY")

# Initialize translator (no need to create instance, it's stateless)
translator = GoogleTranslator(source='en', target='ta')

# Debug output
if ELEVENLABS_API_KEY:
    print(f"✓ ElevenLabs API Key loaded in voice_of_the_doctor.py (length: {len(ELEVENLABS_API_KEY)} characters)")
else:
    print("✗ ElevenLabs API Key NOT found in voice_of_the_doctor.py - will use Google TTS fallback")


def translate_text(text, target_lang):
    """
    Translate text to target language using Google Translate (via deep-translator)
    """
    try:
        # Map full language names to codes if necessary, or assume codes are passed
        # For simplicity, let's assume we might get full names or codes, but deep-translator expects codes.
        # A simple mapping for Indian languages:
        lang_map = {
            'english': 'en', 'tamil': 'ta', 'hindi': 'hi', 'telugu': 'te', 
            'kannada': 'kn', 'malayalam': 'ml', 'bengali': 'bn', 'gujarati': 'gu',
            'marathi': 'mr', 'punjabi': 'pa'
        }
        
        lang_code = lang_map.get(target_lang.lower(), target_lang.lower())
        
        if lang_code == 'en':
            return text

        translator = GoogleTranslator(source='auto', target=lang_code)
        translated_text = translator.translate(text)
        print(f"📝 Translated to {target_lang} ({lang_code}): {translated_text[:100]}...")
        return translated_text
    except Exception as e:
        print(f"✗ Translation Error: {e}")
        print("⚠ Using original text as fallback")
        return text


def text_to_speech_with_gtts(input_text, output_filepath, language='en'):
    """
    Convert text to speech using Google TTS
    """
    print(f"🔊 gTTS called for language={language}")
    
    # Map common names to gTTS codes
    lang_map = {
        'english': 'en', 'tamil': 'ta', 'hindi': 'hi', 'telugu': 'te', 
        'kannada': 'kn', 'malayalam': 'ml', 'bengali': 'bn', 'gujarati': 'gu',
        'marathi': 'mr', 'punjabi': 'pa'
    }
    lang_code = lang_map.get(language.lower(), 'en')
    
    try:
        audioobj = gTTS(
            text=input_text,
            lang=lang_code,
            slow=False
        )
        audioobj.save(output_filepath)
        print(f"✓ gTTS: Audio saved to {output_filepath} (language: {lang_code})")
        return output_filepath
    except Exception as e:
        print(f"✗ gTTS Error: {e}")
        return None


def text_to_speech_with_elevenlabs(input_text, output_filepath, language='en'):
    """
    Convert text to speech using ElevenLabs API with fallback to Google TTS.
    Uses eleven_multilingual_v2 for non-English support.
    """
    print(f"🔊 ElevenLabs called for language={language}")
    
    # Check if API key is available
    if not ELEVENLABS_API_KEY:
        print("⚠ ELEVENLABS_API_KEY not found. Using Google TTS instead...")
        return text_to_speech_with_gtts(input_text, output_filepath, language=language)
    
    try:
        print(f"Attempting ElevenLabs TTS with API key: {ELEVENLABS_API_KEY[:10]}...")
        
        client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        
        # Use multilingual model
        model_id = "eleven_multilingual_v2"
        
        audio = client.generate(
            text=input_text,
            voice="Aria",
            output_format="mp3_22050_32",
            model=model_id
        )
        
        elevenlabs.save(audio, output_filepath)
        print(f"✓ ElevenLabs: Audio saved to {output_filepath}")
        return output_filepath
        
    except Exception as e:
        print(f"✗ ElevenLabs Error: {e}")
        print("⚠ Falling back to Google TTS...")
        return text_to_speech_with_gtts(input_text, output_filepath, language=language)


def play_audio(output_filepath):
    """
    Play audio file based on operating system
    """
    os_name = platform.system()
    try:
        if os_name == "Darwin":  # macOS
            subprocess.run(['afplay', output_filepath])
        elif os_name == "Windows":  # Windows
            subprocess.run(['powershell', '-c', f'(New-Object Media.SoundPlayer "{output_filepath}").PlaySync();'])
        elif os_name == "Linux":  # Linux
            subprocess.run(['aplay', output_filepath])
        else:
            raise OSError("Unsupported operating system")
    except Exception as e:
        print(f"An error occurred while trying to play the audio: {e}")


# Legacy function names for backward compatibility
def text_to_speech_with_gtts_old(input_text, output_filepath):
    return text_to_speech_with_gtts(input_text, output_filepath)


def text_to_speech_with_elevenlabs_old(input_text, output_filepath):
    return text_to_speech_with_elevenlabs(input_text, output_filepath)