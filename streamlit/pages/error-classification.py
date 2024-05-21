import streamlit as st

st.text_area(
        "Prompt ",
        "",
        key="placeholder",
)

st.text_input(
        "Error Description",
        "This is a placeholder",
        key="error_description",
)

st.button("Get Feedback to Error", use_container_width=True)

st.write("hello my friend pleas help me im under the water")