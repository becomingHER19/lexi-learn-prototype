import streamlit as st
import os

st.set_page_config(page_title="Lexi Learn", layout="centered")

st.title("📚 Lexi Learn")
st.subheader("Choose a story to begin")

stories = os.listdir("stories")

for story in stories:
    if st.button(story.replace(".txt", "")):
        st.session_state["story"] = story
        st.session_state["page"] = "reader"
        st.switch_page("pages/story_reader.py")
