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



import datetime
import pandas as pd

df['created_at_dt'] = pd.to_datetime(df['created_at'])

today_messages = len(df[df['created_at_dt'].dt.date == datetime.date.today()])
yesterday_messages = len(df[df['created_at_dt'].dt.date == datetime.date.today() - datetime.timedelta(days = 1)])

# st.dataframe(df[df['created_at_dt'].dt.])

col1, col2 = st.columns(2)

with col1:
    st.metric(label="Messages today", value=str(today_messages), delta=str((today_messages-yesterday_messages)/yesterday_messages*100) + "%", help="This metric shows the difference and percentage change in the number of messages sent today compared to yesterday.")

with col2:
    st.metric(label="Total number of messages", value=str(len(df)), help="Im Vergleich zu gestern!")

st.dataframe(df, use_container_width=True)

# st.table(df.head())