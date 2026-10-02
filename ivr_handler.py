
from fastapi import APIRouter, Request, Response
from xml.sax.saxutils import escape
import os

from bhashini_service import text_to_speech


# ============================================================
# ROUTER
# ============================================================

ivr_router = APIRouter(
    prefix="/ivr",
    tags=["IVR"]
)


# ============================================================
# HELPER: GET PUBLIC BASE URL
# ============================================================

def get_public_url(request: Request):
    return str(request.base_url).rstrip("/")


# ============================================================
# HELPER: CREATE TWIML RESPONSE
# ============================================================

def twiml_response(xml: str):
    return Response(
        content=xml,
        media_type="application/xml"
    )


# ============================================================
# 1. INCOMING CALL
# ============================================================

@ivr_router.post("/incoming")
async def incoming_call(request: Request):
    base_url = get_public_url(request)
    gather_url = f"{base_url}/ivr/gather"

    twiml = f"""
<Response>
    <Gather
        input="speech"
        action="{escape(gather_url)}"
        method="POST"
        language="hi-IN"
        speechTimeout="auto"
        actionOnEmptyResult="true">

        <Say language="hi-IN">
            नमस्ते किसान जी। KrishiSetu AI में आपका स्वागत है।
            कृपया बीप के बाद अपनी खेती की समस्या बताएं।
        </Say>

    </Gather>

    <Say language="hi-IN">
        आपकी आवाज़ प्राप्त नहीं हुई।
        कृपया दोबारा कॉल करें। धन्यवाद।
    </Say>
</Response>
"""

    print("Incoming call received")
    print("Gather callback:", gather_url)

    return twiml_response(twiml)


# ============================================================
# 2. PROCESS SPEECH RESULT FROM TWILIO GATHER
# ============================================================

@ivr_router.post("/gather")
async def process_gather(request: Request):
    form = await request.form()

    # Speech recognized by Twilio
    recognized_text = (form.get("SpeechResult") or "").strip()
    confidence = form.get("Confidence")
    call_sid = form.get("CallSid")

    print()
    print("=" * 60)
    print("TWILIO SPEECH RESULT RECEIVED")
    print("=" * 60)
    print("Call SID:", call_sid)
    print("Recognized speech:", recognized_text)
    print("Confidence:", confidence)

    if not recognized_text:
        twiml = """
<Response>
    <Say language="hi-IN">
        क्षमा करें, आपकी समस्या समझ नहीं आई।
        कृपया दोबारा कॉल करें और अपनी समस्या स्पष्ट रूप से बताएं।
    </Say>
</Response>
"""
        return twiml_response(twiml)

    # ========================================================
    # 3. KRISHISETU AI DECISION ENGINE - MVP
    # ========================================================

    text_lower = recognized_text.lower()

    if (
        "पीली" in recognized_text
        or "पीला" in recognized_text
        or "yellow" in text_lower
    ):
        answer = (
            "आपकी गेहूं की फसल में पत्तियां पीली हो रही हैं। "
            "इसका कारण पोषक तत्वों की कमी, अधिक पानी या रोग हो सकता है। "
            "कृपया खेत की मिट्टी और फसल की स्थिति की जांच करें।"
        )

    elif (
        "पानी" in recognized_text
        or "सिंचाई" in recognized_text
        or "irrigation" in text_lower
        or "water" in text_lower
    ):
        answer = (
            "फसल की सिंचाई मिट्टी की नमी और मौसम की स्थिति के अनुसार करें। "
            "खेत में आवश्यकता से अधिक पानी न दें।"
        )

    elif (
        "कीट" in recognized_text
        or "कीड़ा" in recognized_text
        or "कीड़े" in recognized_text
        or "pest" in text_lower
        or "insect" in text_lower
    ):
        answer = (
            "सबसे पहले फसल में कीट की पहचान करें। "
            "कीट की सही पहचान के बाद ही उपयुक्त नियंत्रण उपाय अपनाएं।"
        )

    elif (
        "खाद" in recognized_text
        or "उर्वरक" in recognized_text
        or "fertilizer" in text_lower
    ):
        answer = (
            "उर्वरक का उपयोग मिट्टी की जांच और फसल की आवश्यकता के आधार पर करें। "
            "अनावश्यक रूप से अधिक उर्वरक का प्रयोग न करें।"
        )

    else:
        answer = (
            "आपकी समस्या समझने के लिए धन्यवाद। "
            "KrishiSetu AI फसल, मिट्टी, सिंचाई और कीट संबंधी समस्याओं में "
            "सहायता करता है। अधिक सटीक सलाह के लिए अपनी फसल और समस्या "
            "का विवरण बताएं।"
        )

    print()
    print("KrishiSetu AI Answer:")
    print(answer)

    # ========================================================
    # 4. GENERATE HINDI SPEECH USING BHASHINI TTS
    # ========================================================

    try:
        print()
        print("=" * 60)
        print("GENERATING BHASHINI TTS")
        print("=" * 60)

        audio_response = text_to_speech(
            answer,
            language="hi"
        )

        if not audio_response:
            raise ValueError("BHASHINI returned empty audio.")

        print("Generated audio:", len(audio_response), "bytes")

    except Exception as e:
        print("ERROR during BHASHINI TTS:", str(e))

        twiml = """
<Response>
    <Say language="hi-IN">
        क्षमा करें, अभी आपका जवाब तैयार नहीं हो पाया।
        कृपया कुछ समय बाद दोबारा प्रयास करें।
    </Say>
</Response>
"""
        return twiml_response(twiml)

    # ========================================================
    # 5. SAVE GENERATED AUDIO
    # ========================================================

    output_file = "tts_response.wav"

    try:
        with open(output_file, "wb") as audio_file:
            audio_file.write(audio_response)

        print("TTS response saved:", output_file)

    except OSError as e:
        print("ERROR saving TTS audio:", str(e))

        twiml = """
<Response>
    <Say language="hi-IN">
        क्षमा करें, आपका जवाब चलाया नहीं जा सका।
    </Say>
</Response>
"""
        return twiml_response(twiml)

    # ========================================================
    # 6. PLAY BHASHINI AUDIO TO CALLER
    # ========================================================

    base_url = get_public_url(request)
    audio_url = f"{base_url}/ivr/audio"

    twiml = f"""
<Response>
    <Say language="hi-IN">
        आपकी समस्या के लिए KrishiSetu AI का सुझाव है।
    </Say>

    <Play>{escape(audio_url)}</Play>

    <Say language="hi-IN">
        धन्यवाद किसान जी। KrishiSetu AI का उपयोग करने के लिए धन्यवाद।
    </Say>
</Response>
"""

    print("Playing response audio:", audio_url)

    return twiml_response(twiml)


# ============================================================
# 7. SERVE GENERATED BHASHINI AUDIO
# ============================================================

@ivr_router.get("/audio")
async def get_audio():
    audio_file = "tts_response.wav"

    if not os.path.exists(audio_file):
        return Response(
            content="Audio file not found.",
            status_code=404,
            media_type="text/plain"
        )

    try:
        with open(audio_file, "rb") as f:
            audio_data = f.read()

        return Response(
            content=audio_data,
            media_type="audio/wav",
            headers={
                "Cache-Control": "no-store"
            }
        )

    except OSError as e:
        print("ERROR reading TTS audio:", str(e))
        return Response(
            content="Unable to read audio file.",
            status_code=500,
            media_type="text/plain"
        )