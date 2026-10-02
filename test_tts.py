import os
import base64
import requests
from dotenv import load_dotenv

# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

# ============================================================
# BHASHINI CONFIGURATION
# ============================================================

API_KEY = os.getenv("BHASHINI_INFERENCE_API_KEY")

URL = os.getenv(
    "BHASHINI_INFERENCE_URL",
    "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"
)

SERVICE_ID = "ai4bharat/indic-tts-coqui-indo_aryan-gpu--t4"

LANGUAGE = "hi"

TEXT = "आपकी गेहूं की फसल में पत्तियां पीली हो रही हैं।"

OUTPUT_FILE = "tts_output.wav"


# ============================================================
# CHECK API KEY
# ============================================================

if not API_KEY:
    print()
    print("=" * 60)
    print("ERROR: BHASHINI_INFERENCE_API_KEY not found.")
    print("=" * 60)
    exit()

print()
print("=" * 60)
print("BHASHINI TTS TEST")
print("=" * 60)

print("API key loaded successfully.")
print("Language:", LANGUAGE)
print("Text:", TEXT)
print("Service ID:", SERVICE_ID)


# ============================================================
# HEADERS
# ============================================================

headers = {
    "Content-Type": "application/json",
    "Accept": "*/*",
    "Authorization": API_KEY
}


# ============================================================
# TTS PAYLOAD
# ============================================================

payload = {
    "pipelineTasks": [
        {
            "taskType": "tts",
            "config": {
                "language": {
                    "sourceLanguage": LANGUAGE
                },
                "serviceId": SERVICE_ID,
                "gender": "female",
                "samplingRate": 16000
            }
        }
    ],
    "inputData": {
        "input": [
            {
                "source": TEXT
            }
        ]
    }
}


# ============================================================
# SEND REQUEST
# ============================================================

print()
print("Sending text to BHASHINI TTS...")

try:

    response = requests.post(
        URL,
        headers=headers,
        json=payload,
        timeout=60
    )

except requests.exceptions.RequestException as e:

    print()
    print("=" * 60)
    print("ERROR CONNECTING TO BHASHINI")
    print("=" * 60)
    print(e)
    exit()


# ============================================================
# HTTP RESPONSE
# ============================================================

print()
print("HTTP Status:", response.status_code)


# ============================================================
# HANDLE HTTP ERROR
# ============================================================

if response.status_code != 200:

    print()
    print("=" * 60)
    print("BHASHINI TTS REQUEST FAILED")
    print("=" * 60)

    print()
    print("Response:")
    print(response.text)

    exit()


# ============================================================
# PARSE JSON RESPONSE
# ============================================================

try:

    data = response.json()

except ValueError as e:

    print()
    print("=" * 60)
    print("ERROR: BHASHINI RETURNED INVALID JSON")
    print("=" * 60)

    print("Error:", e)
    print()
    print("Raw response:")
    print(response.text)

    exit()


print()
print("BHASHINI response received successfully.")


# ============================================================
# GET PIPELINE RESPONSE
# ============================================================

pipeline_response = data.get("pipelineResponse", [])

if not pipeline_response:

    print()
    print("=" * 60)
    print("ERROR: pipelineResponse IS EMPTY")
    print("=" * 60)

    print()
    print("Full response:")
    print(data)

    exit()


print()
print("Number of pipeline responses:", len(pipeline_response))


# ============================================================
# FIND TTS RESPONSE
# ============================================================

tts_result = None

for item in pipeline_response:

    print()
    print("Task Type:", item.get("taskType"))
    print("Available keys:", list(item.keys()))

    if item.get("taskType") == "tts":

        tts_result = item
        break


# ============================================================
# CHECK TTS RESULT
# ============================================================

if tts_result is None:

    print()
    print("=" * 60)
    print("ERROR: TTS RESULT NOT FOUND")
    print("=" * 60)

    print()
    print("Pipeline response:")
    print(data)

    exit()


# ============================================================
# GET OUTPUT
# ============================================================

output = tts_result.get("output")

print()
print("TTS output type:", type(output))

if output is not None:

    try:
        print("TTS output length:", len(output))
    except TypeError:
        pass


# ============================================================
# FIND AUDIO CONTENT
# ============================================================

audio_content = None


# ------------------------------------------------------------
# NORMAL BHASHINI STRUCTURE
# ------------------------------------------------------------

if isinstance(output, list):

    for item in output:

        if isinstance(item, dict):

            if item.get("audioContent"):

                audio_content = item["audioContent"]

                break


# ------------------------------------------------------------
# FALLBACK: RECURSIVE SEARCH
# ------------------------------------------------------------

def find_audio_content(obj):

    if isinstance(obj, dict):

        if obj.get("audioContent"):

            return obj["audioContent"]

        for value in obj.values():

            result = find_audio_content(value)

            if result:

                return result

    elif isinstance(obj, list):

        for value in obj:

            result = find_audio_content(value)

            if result:

                return result

    return None


if not audio_content:

    audio_content = find_audio_content(data)


# ============================================================
# CHECK AUDIO CONTENT
# ============================================================

if not audio_content:

    print()
    print("=" * 60)
    print("ERROR: audioContent NOT FOUND")
    print("=" * 60)

    print()
    print("TTS result:")
    print(tts_result)

    exit()


print()
print("audioContent found successfully!")
print("Base64 length:", len(audio_content))


# ============================================================
# DECODE BASE64 AUDIO
# ============================================================

try:

    audio_bytes = base64.b64decode(audio_content)

except Exception as e:

    print()
    print("=" * 60)
    print("ERROR DECODING AUDIO")
    print("=" * 60)

    print("Error:", e)

    exit()


# ============================================================
# CHECK AUDIO SIZE
# ============================================================

if not audio_bytes:

    print()
    print("=" * 60)
    print("ERROR: DECODED AUDIO IS EMPTY")
    print("=" * 60)

    exit()


print()
print("Decoded audio size:", len(audio_bytes), "bytes")


# ============================================================
# SAVE AUDIO FILE
# ============================================================

try:

    with open(OUTPUT_FILE, "wb") as f:

        f.write(audio_bytes)

except OSError as e:

    print()
    print("=" * 60)
    print("ERROR SAVING AUDIO FILE")
    print("=" * 60)

    print("Error:", e)

    exit()


# ============================================================
# FINAL SUCCESS
# ============================================================

print()
print("=" * 60)
print("              TTS SUCCESS")
print("=" * 60)

print("Text:", TEXT)
print("Language:", LANGUAGE)
print("Service:", SERVICE_ID)
print("Output:", OUTPUT_FILE)
print("Audio size:", len(audio_bytes), "bytes")

print("=" * 60)

print()
print("TTS audio file created successfully!")
print("You can now play:", OUTPUT_FILE)