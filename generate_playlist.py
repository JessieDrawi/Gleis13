import os
import json
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC
from gtts import gTTS
from pathlib import Path

AUDIO_DIR = "static/audio"
COVER_DIR = "static/covers"
ANNOUNCE_DIR = "static/ansagen_cache"
OUTPUT_FILE = "playlist.json"

# Ordner anlegen, falls nicht vorhanden
os.makedirs(COVER_DIR, exist_ok=True)
os.makedirs(ANNOUNCE_DIR, exist_ok=True)

playlist = []

for filename in os.listdir(AUDIO_DIR):
    if not filename.lower().endswith(".mp3"):
        continue

    path = os.path.join(AUDIO_DIR, filename)

    try:
        tags = EasyID3(path)
        title = tags.get("title", [os.path.splitext(filename)[0]])[0]
        artist = tags.get("artist", ["Unbekannt"])[0]

        # COVER extrahieren
        cover_file = f"{os.path.splitext(filename)[0]}.jpg"
        cover_path = os.path.join(COVER_DIR, cover_file)

        if not os.path.exists(cover_path):
            try:
                audio = ID3(path)
                for tag in audio.values():
                    if isinstance(tag, APIC):
                        with open(cover_path, "wb") as img:
                            img.write(tag.data)
                        break
            except Exception as e:
                cover_file = "placeholder.jpg"

        if not os.path.exists(cover_path):
            cover_file = "placeholder.jpg"

        # ANSAGE generieren
        announcement_filename = f"{os.path.splitext(filename)[0].lower()}.mp3"
        announcement_path = os.path.join(ANNOUNCE_DIR, announcement_filename)

        if not os.path.exists(announcement_path):
            text = f"Jetzt {title} von {artist}"
            tts = gTTS(text=text, lang="de")
            tts.save(announcement_path)
            print(f"✅ Ansage erzeugt für {title}")
        else:
            print(f"⏩ Ansage vorhanden für {title}")

        # TRACK in Playlist einfügen
        playlist.append({
            "file": f"audio/{filename}",
            "title": title,
            "artist": artist,
            "cover": f"covers/{cover_file}"
        })

    except Exception as e:
        print(f"⚠️ Fehler bei {filename}: {e}")

# Playlist speichern
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(playlist, f, ensure_ascii=False, indent=2)

print(f"\n🎧 {len(playlist)} Tracks in {OUTPUT_FILE} gespeichert.")