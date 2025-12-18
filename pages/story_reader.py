import streamlit as st
from utils.tts import speak
from utils.stt import transcribe_audio
from audiorecorder import audiorecorder
import difflib
from pydub import AudioSegment

AudioSegment.converter = r"C:\Users\User\Downloads\ffmpeg\ffmpeg\bin\ffmpeg.exe"
AudioSegment.ffprobe = r"C:\Users\User\Downloads\ffmpeg\ffmpeg\bin\ffprobe.exe"


st.title("📖 Story Reader")

if "story" not in st.session_state:
    st.warning("Please go back and select a story.")
    st.stop()

with open(f"stories/{st.session_state['story']}", "r") as f:
    story_text = f.read()

st.write(story_text)
st.divider()

# Read to Me
if st.button("🔊 Read to Me"):
    audio_file = speak(story_text)
    st.audio(audio_file)

st.divider()

# I Will Read
st.subheader("🎤 I Will Read")

audio = audiorecorder("Start Reading", "Stop Recording")

if len(audio) > 0:
    st.audio(audio.export().read())

    with st.spinner("Listening carefully..."):
        spoken_text = transcribe_audio(audio.export().read())

    st.subheader("What Lexi heard:")
    st.write(spoken_text)

    # Accuracy check
    original_words = story_text.lower().split()
    spoken_words = spoken_text.lower().split()

    matcher = difflib.SequenceMatcher(None, original_words, spoken_words)
    accuracy = matcher.ratio() * 100

    st.metric("Reading Accuracy", f"{accuracy:.1f}%")


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


