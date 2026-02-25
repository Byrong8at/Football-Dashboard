# Launcher
import streamlit as st
import os
import pandas as pd
import numpy as np
from script.load_df import *
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
    
    stats=conv_val(df_Club.loc[df_Club['Club'] == selected_club, 'Stat'].iloc[0])
    
    years = sorted(list(stats.keys()), reverse=True)

    col1, col2, col3 = st.columns([0.3, 1, 1]) #determine distance behind each column

    with col1:
        #st.write(df_Club)
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

    def clean_val(val):
        v = str(val).replace('-', '0').strip()
        return int(v) if v.isdigit() else 0

    def render_stats(year_to_show, key_suffix):
        stat_data = stats.get(year_to_show)
        
        if stat_data and stat_data[0] != "No data":
            current_stat = stat_data[0]

            st.subheader(f"Statistiques de la Saison {year_to_show}")
            
            m_a, m_b, m_c, m_d = st.columns(4)
            m_a.metric("Matches", current_stat['matches'])
            m_b.metric("Victoires", current_stat['wins'])
            m_c.metric("Nuls", clean_val(current_stat['draws']))
            m_d.metric("Défaites", clean_val(current_stat['losses']))

            st.divider()
            
            m_left, m_right = st.columns(2)
            ##Generate Graph
            
            with m_left:
                df_result = pd.DataFrame({
                "Result": ["Victoires", "Nuls", "Défaites"],
                "Value": [current_stat['wins'], clean_val(current_stat['draws']), clean_val(current_stat['losses'])]
                })
                st.write("### Graphique Résultat:")
                fig1 = go.Figure(data=[go.Pie(labels=df_result["Result"], values=df_result["Value"], hole=.3)])
                fig1.update_layout(showlegend=False, height=250, margin=dict(l=10,r=10,b=10,t=10))
                st.plotly_chart(fig1, config={'displayModeBar': False}, key=f"res_{key_suffix}")
            
            with m_right:
                df_goals = pd.DataFrame({
                "Type": ["Marqués", "Encaissés"],
                "Goal": [clean_val(current_stat['Goals_for']), clean_val(current_stat['Goal_Again'])]
                })
                st.write("### Bilan des Buts:")
                fig2 = go.Figure(data=[go.Pie(labels=df_goals["Type"], values=df_goals["Goal"], hole=.3)])
                fig2.update_layout(showlegend=False, height=250, margin=dict(l=10,r=10,b=10,t=10))
                st.plotly_chart(fig2, config={'displayModeBar': False}, key=f"goal_{key_suffix}")
        else:
            st.info("Aucune data existante n'a été trouvé")

    with col2:
        selected_year_1 = st.selectbox("Choisir l'année :", options=years, index=0, key="year1")
        render_stats(selected_year_1, "col2")

    with col3:
        idx_2 = 1 if len(years) > 1 else 0
        selected_year_2 = st.selectbox("Choisir l'année :", options=years, index=idx_2, key="year2")
        render_stats(selected_year_2, "col3")