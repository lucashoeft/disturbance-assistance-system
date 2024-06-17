import streamlit as st
import psycopg2
from pandas import DataFrame

st.set_page_config(
    layout="wide",
    page_title="Auswertung - Assistenzsystem",
    page_icon="https://static.wikia.nocookie.net/minecraft_gamepedia/images/b/b7/Crafting_Table_JE4_BE3.png"
)

st.header("Auswertung", anchor=False)

conn = psycopg2.connect(database = "chat_history",
                        user = "admin",
                        password = "admin",
                        host = "postgres",
                        port = "5432")

conn_disturbances = psycopg2.connect(database = "postgres",
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
    if yesterday_messages > 0:
        delta_yesterday_today = (today_messages-yesterday_messages)/yesterday_messages*100
    else:
        delta_yesterday_today = 0
    st.metric(label="Heutige Chatnachrichten", value=str(today_messages), delta=str(round(delta_yesterday_today,2)) + "%", help="This metric shows the difference and percentage change in the number of messages sent today compared to yesterday.", delta_color="off")

with col2:
    st.metric(label="Insgesamte Anzahl an Chatnachrichten", value=str(len(df)))

# st.dataframe(df, use_container_width=True)

# st.table(df.head())

cursor_disturbances = conn_disturbances.cursor()

cursor_disturbances.execute("""
                            SELECT * FROM disturbances
                            ORDER BY id DESC """)

df_disturbances = DataFrame(cursor_disturbances.fetchall(), columns=['Id', 'Beschreibung der Störung', 'Grund der Störung', 'Lösung der Störung'])

st.divider()

st.subheader("Dokumentierte Störungen", anchor=False)
st.dataframe(df_disturbances, use_container_width=True, hide_index=True)