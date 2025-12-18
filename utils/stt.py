import whisper
import tempfile

model = whisper.load_model("base")

def transcribe_audio(audio_bytes):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        f.write(audio_bytes)
        temp_path = f.name

    result = model.transcribe(temp_path)
    return result["text"]
