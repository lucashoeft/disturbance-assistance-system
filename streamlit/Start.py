import streamlit as st

st.set_page_config(
    # initial_sidebar_state="collapsed",
    layout="wide",
    page_title="Start - Assistenzsystem",
    page_icon="https://static.wikia.nocookie.net/minecraft_gamepedia/images/b/b7/Crafting_Table_JE4_BE3.png"
)

st.header('Industrielles Assistenzsystem',anchor=False)

st.caption("Zur Erkennung, Behebung und Dokumentation von Störungen.")

# st.write("Dies ist ein Assistenzsystem, welches dabei unterstützt, Störungen zu erkennen, zu beheben und zu dokumentieren.")

st.page_link("pages/1-Chat.py", label="Neue Störung")

# st.page_link("http://localhost:8501/Chat?sessionId=" + st.session_state.db_session_id, label="Neue Störung")
