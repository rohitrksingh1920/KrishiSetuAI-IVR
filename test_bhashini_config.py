import os
import requests
from dotenv import load_dotenv

load_dotenv()

ULCA_API_KEY = os.getenv("BHASHINI_ULCA_API_KEY")
USER_ID = os.getenv("BHASHINI_USER_ID")

CONFIG_URL = os.getenv(
    "BHASHINI_CONFIG_URL",
    "https://meity-auth.ulcacontrib.org/ulca/apis/v0/model/getModelsPipeline"
)

# BHASHINI Initial Pipeline
PIPELINE_ID = "64392f96daac500b55c543cd"

print("Connecting to BHASHINI Pipeline Config for TTS...")

headers = {
    "Content-Type": "application/json",
    "ulcaApiKey": ULCA_API_KEY,
    "userID": USER_ID
}

payload = {
    "pipelineTasks": [
        {
            "taskType": "tts",
            "config": {
                "language": {
                    "sourceLanguage": "hi"
                }
            }
        }
    ],
    "pipelineRequestConfig": {
        "pipelineId": PIPELINE_ID
    }
}

try:
    response = requests.post(
        CONFIG_URL,
        headers=headers,
        json=payload,
        timeout=30
    )

    print("\nHTTP Status:", response.status_code)

    print("\nResponse:")
    print(response.text)

    # Extract TTS service ID
    if response.status_code == 200:

        try:
            data = response.json()

            configs = data.get("pipelineResponseConfig", [])

            for config in configs:

                if config.get("taskType") == "tts":

                    print("\n" + "=" * 60)
                    print("TTS CONFIGURATION FOUND")
                    print("=" * 60)

                    for item in config.get("config", []):

                        service_id = item.get("serviceId")

                        if service_id:
                            print("TTS Service ID:", service_id)

                        print("Language:", item.get("language"))

                    print("=" * 60)

        except Exception as e:
            print("Could not parse TTS configuration:", e)

except Exception as e:
    print("\nRequest error:")
    print(e)