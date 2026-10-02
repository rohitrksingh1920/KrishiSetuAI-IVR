import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# BHASHINI CONFIG
# ============================================================

API_KEY = os.getenv("BHASHINI_INFERENCE_API_KEY")

INFERENCE_URL = os.getenv(
    "BHASHINI_INFERENCE_URL",
    "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"
)

ASR_SERVICE_ID = "ai4bharat/conformer-multilingual-indo_aryan-gpu--t4"

TTS_SERVICE_ID = "ai4bharat/indic-tts-coqui-indo_aryan-gpu--t4"


# ============================================================
# HEADERS
# ============================================================

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "*/*",
    "Authorization": API_KEY
}


# ============================================================
# BHASHINI ASR
# ============================================================

def speech_to_text(audio_bytes: bytes, language: str = "hi"):

    audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")

    payload = {
        "pipelineTasks": [
            {
                "taskType": "asr",
                "config": {
                    "language": {
                        "sourceLanguage": language
                    },
                    "serviceId": ASR_SERVICE_ID
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

    response = requests.post(
        INFERENCE_URL,
        headers=HEADERS,
        json=payload,
        timeout=60
    )

    response.raise_for_status()

    data = response.json()

    pipeline_response = data.get("pipelineResponse", [])

    if not pipeline_response:
        raise Exception("BHASHINI ASR returned no pipeline response.")

    output = pipeline_response[0].get("output", [])

    if not output:
        raise Exception("BHASHINI ASR returned no output.")

    text = output[0].get("source")

    if not text:
        raise Exception("BHASHINI ASR returned no recognized text.")

    return text


# ============================================================
# BHASHINI TTS
# ============================================================

def text_to_speech(
    text: str,
    language: str = "hi"
):

    payload = {
        "pipelineTasks": [
            {
                "taskType": "tts",
                "config": {
                    "language": {
                        "sourceLanguage": language
                    },
                    "serviceId": TTS_SERVICE_ID,
                    "gender": "female",
                    "samplingRate": 16000
                }
            }
        ],
        "inputData": {
            "input": [
                {
                    "source": text
                }
            ]
        }
    }

    response = requests.post(
        INFERENCE_URL,
        headers=HEADERS,
        json=payload,
        timeout=60
    )

    response.raise_for_status()

    data = response.json()

    # --------------------------------------------------------
    # Find audioContent
    # --------------------------------------------------------

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

    audio_content = find_audio_content(data)

    if not audio_content:
        raise Exception("BHASHINI TTS returned no audioContent.")

    return base64.b64decode(audio_content)