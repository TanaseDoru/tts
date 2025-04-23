# app.py
import os
from flask import Flask, request, send_file, render_template
import azure.cognitiveservices.speech as speechsdk

app = Flask(__name__)

# Hard-coded Azure Speech credentials
subscription_key = "14RYy8Mq4pzhtSaU3cmsjyowVEDwmCahq9NiqSosE6HUctn9Jor4JQQJ99BDAC5T7U2XJ3w3AAAYACOGpWNi"
region           = "francecentral"

speech_config = speechsdk.SpeechConfig(subscription=subscription_key, region=region)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/download_audio", methods=["POST"])
def download_audio():
    raw_text = request.form.get("text", "").strip()
    if not raw_text:
        return "No text provided", 400

    # Build SSML payload wrapping the user’s message
    ssml = f"""
    <speak version='1.0' xml:lang='ro-RO'>
      <voice name='ro-RO-AlinaNeural'>
        {raw_text}
      </voice>
    </speak>
    """

    # Synthesize SSML to a WAV file on disk
    audio_config = speechsdk.audio.AudioOutputConfig(filename="output_audio.wav")
    synthesizer  = speechsdk.SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=audio_config
    )
    result = synthesizer.speak_ssml_async(ssml).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        return send_file("output_audio.wav", as_attachment=True)
    else:
        err = result.cancellation_details.error_details
        return f"Error synthesizing audio: {err}", 500

if __name__ == "__main__":
    app.run(debug=True)
