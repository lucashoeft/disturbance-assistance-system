import streamlit as st
import psycopg2
from pandas import DataFrame

st.set_page_config(layout="wide")

st.header("Dashboard")

conn = psycopg2.connect(database = "chat_history",
                        user = "admin",
                        password = "admin",
                        host = "postgres",
                        port = "5432")

cursor = conn.cursor()

cursor.execute("""
               SELECT 
                    session_id, 
                    created_at, 
                    message->>'type' as type, 
                    message -> 'data' ->> 'content' as content,
                    message -> 'data' -> 'response_metadata' -> 'model_name' as model
               FROM chat_history
               ORDER BY created_at DESC""")

df = DataFrame(cursor.fetchall(), columns=['session_id', 'created_at', 'type', 'content', 'model'])

st.dataframe(df, use_container_width=True)

st.table(df.head())

st.metric(label="Total number of messages", value=str(len(df)), help="Im Vergleich zu gestern!")

