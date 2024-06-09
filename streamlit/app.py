import streamlit as st


st.set_page_config(
   page_title="Störungsassistent",
   page_icon="https://static.wikia.nocookie.net/minecraft_gamepedia/images/b/b7/Crafting_Table_JE4_BE3.png"
)

hide_decoration_bar_style = '''
    <style>
         header {visibility: hidden;}
         [data-testid="stSidebarCollapseButton"] {visibility: hidden;}
    </style>
'''
st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)

st.logo("https://static.wikia.nocookie.net/minecraft_gamepedia/images/b/b7/Crafting_Table_JE4_BE3.png")

st.header('Assistenzsystem',anchor=False)

st.write("Behebungen von Störungen")