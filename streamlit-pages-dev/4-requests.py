import streamlit as st
import requests
import os

port = os.getenv('PORT')

st.write(port)
api_url = "http://host.docker.internal:8080/"
response = requests.get(api_url)
st.write(response.status_code)
st.write(response.json())
