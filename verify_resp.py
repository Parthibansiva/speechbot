import numpy as np
import librosa
import tensorflow as tf
import os
import soundfile as sf

# Configuration
MODEL_PATH = "/home/nishanth/parthibanproject/speechbot/models/trained_models/Respiratory_sound.keras"
RESP_LABELS = ['Asthma', 'Bronchiectasis', 'Bronchiolitis', 'COPD', 'Healthy', 'LRTI', 'Pneumonia', 'URTI']

def extract_features(audio_path):
    print(f"Extracting features from {audio_path}...")
    y, sr = librosa.load(audio_path, duration=6.0)
    
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
    if mfccs.shape[1] < 259:
        mfccs = np.pad(mfccs, ((0, 0), (0, 259 - mfccs.shape[1])), mode='constant')
    else:
        mfccs = mfccs[:, :259]
    mfccs = mfccs.reshape(1, 20, 259, 1)

    chroma = librosa.feature.chroma_stft(y=y, sr=sr, n_chroma=12)
    if chroma.shape[1] < 259:
        chroma = np.pad(chroma, ((0, 0), (0, 259 - chroma.shape[1])), mode='constant')
    else:
        chroma = chroma[:, :259]
    chroma = chroma.reshape(1, 12, 259, 1)

    mspec = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
    mspec = librosa.power_to_db(mspec, ref=np.max)
    if mspec.shape[1] < 259:
        mspec = np.pad(mspec, ((0, 0), (0, 259 - mspec.shape[1])), mode='constant')
    else:
        mspec = mspec[:, :259]
    mspec = mspec.reshape(1, 128, 259, 1)

    return mfccs, chroma, mspec

def verify():
    print("Step 1: Loading model...")
    try:
        model = tf.keras.models.load_model(MODEL_PATH)
        print("✅ Model loaded successfully.")
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return

    print("\nStep 2: Generating dummy 6s audio...")
    dummy_audio = "dummy_verify.wav"
    fs = 22050
    samples = np.random.uniform(-1, 1, int(fs * 6.0))
    sf.write(dummy_audio, samples, fs)
    print(f"✅ Generated {dummy_audio}")

    print("\nStep 3: Extracting features...")
    mfcc, chroma, mspec = extract_features(dummy_audio)
    print(f"✅ Features extracted. Shapes: MFCC={mfcc.shape}, Chroma={chroma.shape}, MelSpec={mspec.shape}")

    print("\nStep 4: Running prediction...")
    try:
        prediction = model.predict([mfcc, chroma, mspec], verbose=0)
        predicted_class = RESP_LABELS[np.argmax(prediction)]
        confidence = np.max(prediction)
        print(f"✅ Prediction successful!")
        print(f"Result: {predicted_class} ({confidence*100:.2f}%)")
    except Exception as e:
        print(f"❌ Prediction failed: {e}")

    # Cleanup
    if os.path.exists(dummy_audio):
        os.remove(dummy_audio)

if __name__ == "__main__":
    verify()
