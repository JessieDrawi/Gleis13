# app.py
import os
import json
from flask import Flask, request, jsonify, send_from_directory, render_template, redirect
from dotenv import load_dotenv
from pydub import AudioSegment, effects
import openai

# Lade API-Key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
STATIC_FOLDER = os.path.join(os.path.dirname(__file__), "static")
AUDIO_FOLDER = os.path.join(STATIC_FOLDER, "audio")
CACHE_FOLDER = os.path.join(STATIC_FOLDER, "ansagen_cache")
os.makedirs(CACHE_FOLDER, exist_ok=True)

# OpenAI TTS generieren
def generate_tts(text, output_path):
    response = openai.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=text
    )
    with open(output_path, "wb") as f:
        f.write(response.content)

# Bahnhofs-Soundeffekte anwenden
def apply_bahnfx(input_path, output_path):
    voice = AudioSegment.from_file(input_path)
    voice = voice._spawn(voice.raw_data, overrides={
        "frame_rate": int(voice.frame_rate * 0.95)
    }).set_frame_rate(voice.frame_rate)
    voice = voice - 1
    voice = effects.normalize(voice)
    filtered = voice.high_pass_filter(500).low_pass_filter(3000)
    filtered.export(output_path, format="mp3")

# Bahnansage generieren und ggf. cachen
def generate_bahnansage(title, artist):
    safe_title = title.lower().replace(" ", "_")
    safe_artist = artist.lower().replace(" ", "_")
    filename = f"{safe_title}_{safe_artist}.mp3"
    final_path = os.path.join(CACHE_FOLDER, filename)

    if os.path.exists(final_path):
        return f"/static/ansagen_cache/{filename}"

    text = f"Nächster Halt: {title} von {artist}."
    tmp_path = os.path.join(CACHE_FOLDER, "tmp.mp3")
    generate_tts(text, tmp_path)
    apply_bahnfx(tmp_path, final_path)
    return f"/static/ansagen_cache/{filename}"

@app.route("/")
def home():
    return redirect("/radio")

@app.route("/radio")
def radio():
    return render_template("radio.html")

@app.route("/playlist")
def playlist():
    with open("playlist.json", "r", encoding="utf-8") as f:
        return jsonify(json.load(f))

@app.route("/generate_for_song")
def generate_for_song():
    title = request.args.get("title")
    artist = request.args.get("artist")
    if not title or not artist:
        return "Fehlende Parameter", 400
    url = generate_bahnansage(title, artist)
    return redirect(url)

@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory(STATIC_FOLDER, filename)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
