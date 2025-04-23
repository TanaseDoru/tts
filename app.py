import os
import uuid
from flask import Flask, request, send_file, render_template, jsonify
import azure.cognitiveservices.speech as speechsdk

app = Flask(__name__)

# Use environment variables for credentials, fallback to hard-coded if not set
subscription_key = os.getenv("AZURE_SPEECH_KEY", "14RYy8Mq4pzhtSaU3cmsjyowVEDwmCahq9NiqSosE6HUctn9Jor4JQQJ99BDAC5T7U2XJ3w3AAAYACOGpWNi")
region           = os.getenv("AZURE_SPEECH_REGION", "francecentral")

speech_config = speechsdk.SpeechConfig(subscription=subscription_key, region=region)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/synthesize", methods=["POST"])
def synthesize():
    payload = request.get_json(force=True)
    raw_text = payload.get("text", "").strip()
    if not raw_text:
        return jsonify({"error": "No text provided"}), 400

    # Build SSML
    ssml = f"""
    <speak version='1.0' xml:lang='ro-RO'>
      <voice name='ro-RO-AlinaNeural'>
        {raw_text}
      </voice>
    </speak>
    """

    # Generate a unique filename to avoid collisions
    filename = f"output_{uuid.uuid4().hex}.wav"
    audio_config = speechsdk.audio.AudioOutputConfig(filename=filename)
    synthesizer  = speechsdk.SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=audio_config
    )
    result = synthesizer.speak_ssml_async(ssml).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        # Read WAV data and clean up
        with open(filename, 'rb') as f:
            data = f.read()
        os.remove(filename)

        # Return WAV data inline for playback and download
        return (data, 200, {
            'Content-Type': 'audio/wav',
            'Content-Disposition': 'inline; filename="speech.wav"'
        })
    else:
        err = result.cancellation_details.error_details
        return jsonify({"error": err}), 500

if __name__ == "__main__":
    app.run(debug=True)