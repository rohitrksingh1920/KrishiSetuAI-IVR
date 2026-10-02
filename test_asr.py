import os
import base64
import requests
from dotenv import load_dotenv

# Load .env
load_dotenv()

# --------------------------------------------------
# BHASHINI CONFIG
# --------------------------------------------------

API_KEY = os.getenv("BHASHINI_INFERENCE_API_KEY")

URL = "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"

SERVICE_ID = "ai4bharat/conformer-multilingual-indo_aryan-gpu--t4"

LANGUAGE = "hi"

# Change this to the name of your audio file
AUDIO_FILE = "test_audio.wav"


# --------------------------------------------------
# CHECK API KEY
# --------------------------------------------------

if not API_KEY:
    print("ERROR: BHASHINI_INFERENCE_API_KEY not found in .env")
    exit()

print("BHASHINI API key loaded.")
print("Preparing audio...")


# --------------------------------------------------
# READ AUDIO FILE
# --------------------------------------------------

if not os.path.exists(AUDIO_FILE):
    print(f"ERROR: Audio file not found: {AUDIO_FILE}")
    print()
    print("Put a WAV audio file in the same folder as test_asr.py")
    print("Example:")
    print("KrishiSetuAI-IVR/")
    print("├── test_asr.py")
    print("└── test_audio.wav")
    exit()


with open(AUDIO_FILE, "rb") as audio_file:
    audio_bytes = audio_file.read()

audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")

print(f"Audio loaded: {AUDIO_FILE}")
print(f"Audio size: {len(audio_bytes)} bytes")
print("Sending audio to BHASHINI ASR...")


# --------------------------------------------------
# REQUEST HEADERS
# --------------------------------------------------

headers = {
    "Content-Type": "application/json",
    "Accept": "*/*",
    "Authorization": API_KEY
}


# --------------------------------------------------
# BHASHINI ASR REQUEST
# --------------------------------------------------

payload = {
    "pipelineTasks": [
        {
            "taskType": "asr",
            "config": {
                "language": {
                    "sourceLanguage": LANGUAGE
                },
                "serviceId": SERVICE_ID
            }
        }
    ],
    "inputData": {
        "audio": [
            {
                "audioContent": audio_base64
            }
        ]
    }
}


# --------------------------------------------------
# CALL BHASHINI
# --------------------------------------------------

try:

    response = requests.post(
        URL,
        headers=headers,
        json=payload,
        timeout=60
    )

    print()
    print("HTTP Status:", response.status_code)
    print()

    # Print complete response for debugging
    print("BHASHINI Response:")
    print(response.text)

    # --------------------------------------------------
    # PROCESS SUCCESS RESPONSE
    # --------------------------------------------------

    if response.status_code == 200:

        data = response.json()

        try:
            output = data["pipelineResponse"][0]["output"][0]

            print()
            print("=" * 50)
            print("ASR SUCCESS")
            print("=" * 50)

            print("Recognized text:")

            if "source" in output:
                print(output["source"])
            elif "target" in output:
                print(output["target"])
            else:
                print(output)

            print("=" * 50)

        except (KeyError, IndexError, TypeError):

            print()
            print("Request succeeded, but the response format")
            print("was different from the expected structure.")

    else:

        print()
        print("BHASHINI ASR request failed.")
        print("Check the HTTP status and response above.")


except requests.exceptions.RequestException as e:

    print()
    print("ERROR connecting to BHASHINI:")
    print(e)