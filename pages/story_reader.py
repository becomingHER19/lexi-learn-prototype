import streamlit as st
from utils.tts import speak
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase
import numpy as np
import queue
import difflib
import tempfile
import whisper
import soundfile as sf

# ---------- AUDIO PROCESSOR ----------
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.audio_buffer = queue.Queue()

    def recv_audio(self, frame):
        audio = frame.to_ndarray()
        self.audio_buffer.put(audio)
        return frame


# ---------- APP UI ----------
st.title("📖 Story Reader")

if "story" not in st.session_state:
    st.warning("Please go back and select a story.")
    st.stop()

with open(f"stories/{st.session_state['story']}", "r") as f:
    story_text = f.read()

st.write(story_text)
st.divider()

# ---------- READ TO ME ----------
if st.button("🔊 Read to Me"):
    audio_file = speak(story_text)
    st.audio(audio_file)

st.divider()

# ---------- I WILL READ ----------
st.subheader("🎤 I Will Read")
st.write("Click start, read the story aloud, then click **Stop Reading**.")

# Start mic stream
ctx = webrtc_streamer(
    key="speech",
    audio_processor_factory=AudioProcessor,
    media_stream_constraints={"audio": True, "video": False},
)

# Stop button
if st.button("Stop Reading"):
    st.session_state.recording_done = True

spoken_text = None

# Analyze ONLY after stop
if ctx.audio_processor and st.session_state.recording_done:
    st.info("Analyzing your reading...")

    audio_chunks = []
    while not ctx.audio_processor.audio_buffer.empty():
        audio_chunks.append(ctx.audio_processor.audio_buffer.get())

    if len(audio_chunks) < 3:
        st.warning("Please read a little longer before stopping.")
    else:
        audio_np = np.concatenate(audio_chunks, axis=0)

        # Save audio
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            sf.write(f.name, audio_np, 16000)
            audio_path = f.name

        # Transcribe
        model = whisper.load_model("tiny")
        result = model.transcribe(audio_path)
        spoken_text = result["text"]

        st.subheader("What Lexi heard:")
        st.write(spoken_text)

 #accuracy
if spoken_text:
    original_words = story_text.lower().split()
    spoken_words = spoken_text.lower().split()

    matcher = difflib.SequenceMatcher(None, original_words, spoken_words)
    accuracy = matcher.ratio() * 100

    st.metric("Reading Accuracy", f"{accuracy:.1f}%")

    missed_words = [w for w in original_words if w not in spoken_words]

    if missed_words:
        st.write("❌ Missed words:")
        st.write(", ".join(missed_words[:10]))
    else:
        st.write("✅ No missed words detected")

# ---------- COMPREHENSION ----------
st.divider()
st.subheader("🧠 Check Your Understanding")

questions = [
    {
        "q": "Who was the main character in the story?",
        "options": ["A fox", "A dog", "A bird"],
        "answer": "A fox"
    },
    {
        "q": "How was the fox feeling?",
        "options": ["Happy", "Hungry", "Angry"],
        "answer": "Hungry"
    },
    {
        "q": "What lesson did the fox learn?",
        "options": ["Be kind", "Be patient", "Think smart"],
        "answer": "Think smart"
    }
]

score = 0
for i, item in enumerate(questions):
    user_ans = st.radio(item["q"], item["options"], key=i)
    if user_ans == item["answer"]:
        score += 1

if st.button("Submit Answers"):
    st.success(f"You got {score} out of {len(questions)} correct!")

    if score == len(questions):
        st.balloons()
        st.write("🌟 Excellent understanding!")
    elif score >= 2:
        st.write("👍 Good job! Let’s keep practicing.")
    else:
        st.write("📖 Let’s read the story again together.")

