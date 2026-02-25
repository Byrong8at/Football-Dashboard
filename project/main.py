# Launcher
import streamlit as st
import os
import pandas as pd
import numpy as np
from script.load_df import load_csv,clean_val
import ast
import plotly.graph_objects as go

# Page Configuration
st.set_page_config(page_title="Football Dashboard", layout="wide")

st.title("Football Dashboard")

@st.cache_data
def Load_data(name):
    return load_csv(name,os.path.dirname(os.path.abspath(__file__)))

df_Club=Load_data("Clubs.csv")

selected_club = st.selectbox(
        "Select the Club:",
        options=df_Club['Club'],
        index=None,
        placeholder="Choose a club..."
    )

if selected_club!=None:
    col1, col2 = st.columns([0.3, 1])#determine distance behind each column

    with col1:
        #st.write(df_Club.head())
        logo_url = df_Club.loc[df_Club['Club'] == selected_club, 'Team_Icon'].iloc[0]

        st.markdown(
            f"""
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center;">
                <img src="{logo_url}" width="200px">
                <h3 style="margin-top: 0px;">{selected_club}</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:

        stats=df_Club.loc[df_Club['Club'] == selected_club, 'Stat'].iloc[0]
        if isinstance(stats, str):
            stats_list = ast.literal_eval(stats)

        stats = stats_list[0]


        st.subheader("Statistiques de la Saison")
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Matches", stats['matches'])
        m2.metric("Victoires", stats['wins'])
        try:
            m3.metric("Nuls", clean_val(stats['draws']))
            m4.metric("Défaites", clean_val(stats['losses']))
        except:
            m3.metric("Nuls", stats['draws'])
            m4.metric("Défaites", stats['losses'])

        st.divider()
        
        m5, m6 = st.columns(2)
        ##Generate Graph
        
        with m5:
            df_result = pd.DataFrame({
            "Result": ["Victoires", "Nuls", "Défaites"],
            "Value": [stats['wins'], stats['draws'], stats['losses']]
            })
            st.write("### Graphique Résultat:")
            fig1 = go.Figure(data=[go.Pie(labels=df_result["Result"], values=df_result["Value"], hole=.3)])
            st.plotly_chart(fig1, config={'displayModeBar': False})
        with m6:
            df_goals = pd.DataFrame({
            "Type": ["Marqués", "Encaissés"],
            "Goal": [stats['Goals_for'], stats['Goal_Again']]
            })

            fig = go.Figure(data=[go.Pie(labels=df_goals["Type"], values=df_goals["Goal"], hole=.3)])
            st.write("### Bilan des Buts:")
            st.plotly_chart(fig,  config={'displayModeBar': False})