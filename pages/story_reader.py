import streamlit as st
from audiorecorder import audiorecorder
import tempfile
import whisper
import difflib
import numpy as np
import soundfile as sf

# ---------------- LOAD WHISPER ONCE ----------------
@st.cache_resource
def load_whisper():
    return whisper.load_model("tiny")

# ---------------- APP START ----------------
st.set_page_config(page_title="Lexi – Story Reader", layout="centered")
st.title("📖 Story Reader")

# ---------------- STORY LOAD ----------------
if "story" not in st.session_state:
    st.warning("Please go back and select a story.")
    st.stop()

with open(f"stories/{st.session_state['story']}", "r", encoding="utf-8") as f:
    story_text = f.read()

st.subheader("📘 Story")
st.write(story_text)

st.divider()

# ---------------- READ TO ME ----------------
st.subheader("🔊 Read to Me")

if st.button("Read Aloud"):
    # Placeholder: your existing TTS function
    st.info("TTS plays here (already working in your app).")

st.divider()

# ---------------- I WILL READ ----------------
st.subheader("🎤 I Will Read")
st.write("Press **Start Recording**, read the story aloud, then press **Stop Recording**.")

audio = audiorecorder("Start Recording", "Stop Recording")

spoken_text = None

if len(audio) > 0:
    st.audio(audio.export().read())

    # Convert audio to numpy
    samples = np.array(audio.get_array_of_samples()).astype(np.float32)
    samples /= 32768.0  # normalize

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        sf.write(f.name, samples, audio.frame_rate)
        audio_path = f.name

    st.info("Analyzing your reading...")

    model = load_whisper()
    result = model.transcribe(audio_path)
    spoken_text = result["text"]

    st.subheader("What Lexi heard:")
    st.write(spoken_text)

# ---------------- ACCURACY + MISSED WORDS ----------------
if spoken_text:
    original_words = story_text.lower().split()
    spoken_words = spoken_text.lower().split()

    matcher = difflib.SequenceMatcher(None, original_words, spoken_words)
    accuracy = matcher.ratio() * 100

    st.metric("📊 Reading Accuracy", f"{accuracy:.1f}%")

    missed_words = [w for w in original_words if w not in spoken_words]

    if missed_words:
        st.write("❌ Missed words:")
        st.write(", ".join(missed_words[:10]))
    else:
        st.success("✅ No missed words detected")

# ---------------- COMPREHENSION ----------------
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
    user_ans = st.radio(item["q"], item["options"], key=f"q{i}")
    if user_ans == item["answer"]:
        score += 1

if st.button("Submit Answers"):
    st.success(f"You got {score} out of {len(questions)} correct!")

    if score == len(questions):
        st.balloons()
        st.write("🌟 Excellent understanding!")
    elif score >= 2:
        st.write("👍 Good job! Keep practicing.")
    else:
        st.write("📖 Let’s read the story again together.")

