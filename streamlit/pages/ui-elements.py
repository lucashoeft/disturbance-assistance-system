import streamlit as st
import time

with st.sidebar:
    st.button("Create New Error")

    with st.echo():
        st.write("This code will be printed to the sidebar.")

    with st.spinner("Loading..."):
        time.sleep(5)
    
    st.success("Done!")

st.page_link("pages/error-classification.py", label="Error Classification", icon="1️⃣")

st.radio(
            "Radio Buttons",
            options=["Option 1", "Option 2", "Option 3"],

)

st.button("Click Me")

st.text_input(
            "Text Input Widget",
            "This is a placeholder",
)