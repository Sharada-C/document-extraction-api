import requests
import base64
import json
import os

# CONFIGURATION
FILE_PATH = "sample1-Technology Industry Analysis.pdf" 
FILE_TYPE = "pdf" 
# Replace your localhost URL with this one:
URL = "https://document-extraction-api-39s3.onrender.com/api/document-analyze"
API_KEY = "sk_track2_987654321"

def run_test():
    print(f"--- Starting Test for {FILE_PATH} ---")
    
    # 1. Check if file exists
    if not os.path.exists(FILE_PATH):
        print(f"ERROR: File '{FILE_PATH}' not found in {os.getcwd()}")
        return

    # 2. Encode File
    try:
        with open(FILE_PATH, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode('utf-8')
        print("Successfully encoded file to Base64.")
    except Exception as e:
        print(f"ERROR during encoding: {e}")
        return

    # 3. Prepare Request
    payload = {
        "fileName": FILE_PATH,
        "fileType": FILE_TYPE,
        "fileBase64": encoded_string
    }
    headers = {"x-api-key": API_KEY}

    # 4. Send Request
    print(f"Sending POST request to {URL}...")
    try:
        response = requests.post(URL, json=payload, headers=headers, timeout=60)
        print(f"Response Status Code: {response.status_code}")
        print("Response JSON:")
        print(json.dumps(response.json(), indent=4))
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to the server. Is Uvicorn running in Terminal 1?")
    except Exception as e:
        print(f"ERROR during request: {e}")

if __name__ == "__main__":
    run_test()