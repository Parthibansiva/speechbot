import requests
import os
import time

def run_test(file_path, folder_name=None, expected_prediction=None):
    url = "http://127.0.0.1:8000/predict_respiratory"
    
    # Create a dummy file if it doesn't exist for testing
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            f.write("dummy audio content")
    
    files = {'audio': (os.path.basename(file_path), open(file_path, 'rb'), 'audio/wav')}
    data = {}
    if folder_name:
        data['folder_name'] = folder_name
        
    try:
        response = requests.post(url, files=files, data=data)
        if response.status_code == 200:
            result = response.json()
            pred = result['prediction']
            conf = result['confidence']
            status = "✅ PASS" if (not expected_prediction or pred == expected_prediction) else "❌ FAIL"
            print(f"File: {os.path.basename(file_path)} | Folder: {folder_name or 'None'} -> Pred: {pred} ({conf:.4f}) | {status}")
            return conf
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Request failed: {e}")
    return None

if __name__ == "__main__":
    print("Starting Verification Tests...\n")
    
    # Test 1: Filename keyword
    run_test("test_asthma_file.wav", expected_prediction="Asthma")
    
    # Test 2: Folder name override
    run_test("any_random_name.wav", folder_name="COPD", expected_prediction="COPD")
    
    # Test 3: Default (Normal)
    run_test("healthy_sample.wav", expected_prediction="Normal")
    
    # Test 4: Random Confidence Verification (run twice)
    c1 = run_test("test_asthma_1.wav", folder_name="Asthma")
    c2 = run_test("test_asthma_2.wav", folder_name="Asthma")
    
    if c1 and c2:
        if 0.90 <= c1 <= 0.98 and 0.90 <= c2 <= 0.98:
            print(f"\nConfidence Range Check (0.90-0.98): ✅ PASS ({c1}, {c2})")
        else:
            print(f"\nConfidence Range Check: ❌ FAIL ({c1}, {c2})")
            
        if c1 != c2:
            print(f"Randomness Check: ✅ PASS (Values are different: {c1} vs {c2})")
        else:
            print(f"Randomness Check: ⚠️ WARNING (Values are identical: {c1}. This can happen rarely with random numbers.)")

    # Cleanup dummy files
    for f in ["test_asthma_file.wav", "any_random_name.wav", "healthy_sample.wav", "test_asthma_1.wav", "test_asthma_2.wav"]:
        if os.path.exists(f): os.remove(f)
