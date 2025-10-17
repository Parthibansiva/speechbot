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


def translate_to_tamil(english_text):
    """
    Translate English text to Tamil using Google Translate (via deep-translator)
    """
    try:
        tamil_text = translator.translate(english_text)
        print(f"📝 Translated to Tamil: {tamil_text[:100]}...")
        return tamil_text
    except Exception as e:
        print(f"✗ Translation Error: {e}")
        print("⚠ Using original English text as fallback")
        return english_text


def text_to_speech_with_gtts_tamil(tamil_text, output_filepath):
    """
    Helper function to speak already-translated Tamil text
    """
    try:
        audioobj = gTTS(
            text=tamil_text,
            lang='ta',
            slow=False
        )
        audioobj.save(output_filepath)
        print(f"✓ gTTS: Tamil audio saved to {output_filepath}")
        return output_filepath
    except Exception as e:
        print(f"✗ gTTS Error: {e}")
        return None


def text_to_speech_with_gtts(input_text, output_filepath, translate=True):
    """
    Convert text to speech using Google TTS
    If translate=True, translates English to Tamil first
    """
    print(f"🔊 gTTS called with translate={translate}")
    
    # Translate to Tamil if requested
    if translate:
        print(f"📥 Original text: {input_text[:100]}...")
        text_to_speak = translate_to_tamil(input_text)
        language = 'ta'
    else:
        text_to_speak = input_text
        language = 'en'
    
    try:
        audioobj = gTTS(
            text=text_to_speak,
            lang=language,
            slow=False
        )
        audioobj.save(output_filepath)
        print(f"✓ gTTS: Audio saved to {output_filepath} (language: {language})")
        return output_filepath
    except Exception as e:
        print(f"✗ gTTS Error: {e}")
        return None


def text_to_speech_with_elevenlabs(input_text, output_filepath, translate=True):
    """
    Convert text to speech using ElevenLabs API with fallback to Google TTS
    If translate=True, translates English to Tamil first
    """
    print(f"🔊 ElevenLabs called with translate={translate}")
    
    # Translate to Tamil if requested
    if translate:
        print(f"📥 Original text: {input_text[:100]}...")
        text_to_speak = translate_to_tamil(input_text)
    else:
        text_to_speak = input_text
    
    # Check if API key is available
    if not ELEVENLABS_API_KEY:
        print("⚠ ELEVENLABS_API_KEY not found. Using Google TTS instead...")
        return text_to_speech_with_gtts(text_to_speak, output_filepath, translate=False)
    
    try:
        print(f"Attempting ElevenLabs TTS with API key: {ELEVENLABS_API_KEY[:10]}...")
        
        client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        
        audio = client.generate(
            text=text_to_speak,
            voice="Aria",
            output_format="mp3_22050_32",
            model="eleven_turbo_v2"
        )
        
        elevenlabs.save(audio, output_filepath)
        print(f"✓ ElevenLabs: Audio saved to {output_filepath}")
        return output_filepath
        
    except elevenlabs.core.api_error.ApiError as e:
        print(f"✗ ElevenLabs API Error: {e}")
        print("⚠ Falling back to Google TTS with translated text...")
        # text_to_speak is already translated, so use translate=False and set language='ta'
        return text_to_speech_with_gtts_tamil(text_to_speak, output_filepath)
        
    except Exception as e:
        print(f"✗ ElevenLabs Error: {e}")
        print("⚠ Falling back to Google TTS with translated text...")
        return text_to_speech_with_gtts_tamil(text_to_speak, output_filepath)


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