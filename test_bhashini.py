import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("BHASHINI_INFERENCE_API_KEY")

URL = "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"


def test_bhashini():

    if not API_KEY:
        print("❌ BHASHINI_INFERENCE_API_KEY is missing")
        return

    headers = {
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Authorization": API_KEY
    }

    payload = {
        "pipelineTasks": [
            {
                "taskType": "translation",
                "config": {
                    "language": {
                        "sourceLanguage": "hi",
                        "targetLanguage": "en"
                    },
                    "serviceId": "ai4bharat/indictrans-v2-all-gpu--t4"
                }
            }
        ],
        "inputData": {
            "input": [
                {
                    "source": "नमस्ते"
                }
            ]
        }
    }

    print("\n🔄 Connecting to BHASHINI...")
    print("📡 Sending test request...")

    try:

        response = requests.post(
            URL,
            headers=headers,
            json=payload,
            timeout=60
        )

        print("\nHTTP Status:", response.status_code)

        try:
            data = response.json()
        except Exception:
            print(response.text)
            return

        if response.status_code == 200:

            print("\n✅ BHASHINI API is working!")

            print("\nResponse:")
            print(data)

            try:
                translated = (
                    data["pipelineResponse"][0]
                    ["output"][0]
                    ["target"]
                )

                print("\n🇮🇳 Hindi:")
                print("नमस्ते")

                print("\n🇬🇧 English:")
                print(translated)

            except Exception:
                print("\n⚠️ API worked, but response format was different.")

        else:

            print("\n❌ BHASHINI API request failed.")
            print("\nResponse:")
            print(data)

    except requests.exceptions.Timeout:

        print("\n❌ Request timed out.")

    except requests.exceptions.RequestException as e:

        print("\n❌ Request error:")
        print(e)


if __name__ == "__main__":
    test_bhashini()