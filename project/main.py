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

parent_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(parent_dir, "src", "logo.png")
st.sidebar.image(logo_path,width=100)
st.sidebar.title("Football Dashboard")

@st.cache_data
def Load_data():
    return load_all_csv(os.path.dirname(os.path.abspath(__file__)))

df_Club = Load_data()

if df_Club.empty:
    st.error("Aucune donnée trouvée. Veuillez vérifier le dossier 'data'.")
    st.stop()

selected_club = st.sidebar.selectbox(
    "Selectionne le Club:",
    options=sorted(df_Club['Club'].unique()),
    index=None,
    placeholder="Choisit le club..."
)

if selected_club != None:
    st.write(df_Club)
    df_selected = df_Club[df_Club['Club'] == selected_club]
    
    stats = {}
    data_dict = {}
    
    for _, row in df_selected.iterrows():
        annee = row['Year']
        stats[annee] = conv_val(row['Stat'])
        data_dict[annee] = conv_val(row['Match_Stat'])
        
    years = sorted(list(stats.keys()), reverse=True)
    
    col_logo, col_info = st.columns([0.2, 0.8])
    logo_url = df_selected['Team_Icon'].iloc[0]
    
    with col_logo:
        st.image(logo_url, width=120)
    with col_info:
        st.title(selected_club)
        st.write("Analyse des performances par saison et détails des rencontres.")

    st.divider()

    def clean_val_loc(val):
        v = str(val).replace('-', '0').strip()
        return int(v) if v.isdigit() else 0

    def render_stats(year_to_show, key_suffix):
        stat_data = stats.get(year_to_show)
        if stat_data and stat_data[0] != "No data":
            current_stat = stat_data[0]
            st.subheader(f"Saison {year_to_show+1}")
            
            m_a, m_b, m_c, m_d = st.columns(4)
            m_a.metric("Matches", current_stat['matches'])
            m_b.metric("Victoires", current_stat['wins'])
            m_c.metric("Nuls", clean_val_loc(current_stat['draws']))
            m_d.metric("Défaites", clean_val_loc(current_stat['losses']))

            fig = go.Figure()
            fig.add_trace(go.Pie(
                labels=["Victoires", "Nuls", "Défaites"],
                values=[current_stat['wins'], clean_val_loc(current_stat['draws']), clean_val_loc(current_stat['losses'])],
                hole=.4,
                marker=dict(colors=['#28a745', '#ffc107', '#dc3545'])
            ))
            fig.update_layout(height=220, margin=dict(l=10,r=10,b=10,t=10), showlegend=True)
            st.plotly_chart(fig, use_container_width=True, key=f"pie_{key_suffix}")
        else:
            st.info("Données de résumé indisponibles.")

    c1, c2 = st.columns(2)
    with c1:
        sel_y1 = st.selectbox("Comparer Saison :", options=years, index=0, key="y1", format_func=lambda x: f"{int(x)+1}")
        render_stats(sel_y1, "left")
    with c2:
        idx_2 = 1 if len(years) > 1 else 0
        sel_y2 = st.selectbox("Avec Saison :", options=years, index=idx_2, key="y2", format_func=lambda x: f"{int(x)+1}")
        render_stats(sel_y2, "right")


    def display_metric_row(label_value_pairs, cols_count=4):
        cols = st.columns(cols_count)
        for col, (label, value) in zip(cols, label_value_pairs):
            col.metric(label, value)

    def Get_match_Year(df_matchs,selected_year_1):
        container1=st.expander(f"Saison {selected_year_1+1}:")
        with container1:
            try:
                competition=list(np.unique(df_matchs['Type']))
                for mtc in competition:
                    
                    df_filtre = df_matchs[df_matchs['Type'] == mtc]
                    url = df_filtre["Icon"].iloc[0]
                    st.markdown(f"![icon]({url}) **{mtc}:**", unsafe_allow_html=True)
                    df_display = df_filtre[[
                    "Matches", "Date", "Time", "Venue", "Rank", 
                    "Opponent", "System", "Attendance", "Score"
                    ]].copy()
                    
                    df_display.columns = [
                        "Journée", "Date", "Heure", "Lieu", "Rang", 
                        "Adversaire", "Système", "Publique", "Score"
                    ]
                    victory=0
                    draw=0
                    defeat=0
                    goals=0
                    goal_h=0
                    goal_a=0
                    goal_lost_h=0
                    goal_lost_a=0
                    victory_h=0
                    victory_a=0
                    draw_h=0
                    draw_a=0
                    defeat_h=0
                    defeat_a=0

                    
                    for index, row in df_display.iterrows():
                        score = str(row['Score']).strip()
                        lieu = row['Lieu']

                        if score != "-:-" and ":" in score:
                            try:
                                parties = score.split(':')                    
                                score_home = int(re.search(r'\d+', parties[0]).group())
                                score_away = int(re.search(r'\d+', parties[1]).group())
                                if lieu == "H":
                                    goal_h += score_home
                                    goal_lost_h+=score_away
                                    if score_home == score_away:
                                        draw_h += 1
                                    elif score_home > score_away:
                                        victory_h += 1
                                    else:
                                        defeat_h += 1
                                else:
                                    goal_a += score_away
                                    goal_lost_a+=score_home
                                    if score_home == score_away:
                                        draw_a += 1
                                    elif score_away > score_home:
                                        victory_a += 1
                                    else:
                                        defeat_a += 1
                                goals=goals+score_away+score_home
                                if score_home == score_away:
                                    draw += 1
                                elif (lieu == "H" and score_home > score_away) or (lieu == "A" and score_away > score_home):
                                    victory += 1
                                else:
                                    defeat += 1
                            except Exception as e:
                                st.write(e)
                                continue 
                    df_display['Publique'] = pd.to_numeric(df_display['Publique'].astype(str).str.replace('.', ''), errors='coerce').fillna(0)
                    system=df_display['Système'].value_counts().idxmax()
                    supporter=df_display.loc[df_display['Lieu'] == "H",'Publique'].sum()
                    if mtc not in ["Korean Super Cup","K League 1 Promotion Playoff", "Korea Cup","FIFA Club World Cup","AFC Champions League Elite","AFC Champions League Two"]:
                            def get_pts(row):
                                s = str(row['Score'])
                                if "-:-" in s or ":" not in s: return 0
                                p = s.split(':')
                                sh = int(re.search(r'\d+', p[0]).group())
                                sa = int(re.search(r'\d+', p[1]).group())
                                if sh == sa: return 1
                                if (row['Lieu'] == "H" and sh > sa) or (row['Lieu'] == "A" and sa > sh): return 3
                                return 0

                            df_display['Point'] = df_display.apply(get_pts, axis=1)
                            state=True
                            df_chart = df_display.sort_values("Journée").copy()
                            df_chart['Points Cumulés'] = df_chart['Point'].cumsum()
                    else:
                        state=False
                    if mtc not in ["Korean Super Cup"]:
                        df_scores = df_display[df_display['Score'].str.strip() != "-:-"]
                        result = df_scores['Score'].value_counts().reset_index()
                        result.columns = ['Score', 'apparition']

                    df_display = style_df(df_display)
                    st.dataframe(df_display, use_container_width=True, hide_index=True)
                    matches=victory+defeat+draw
                    matches_h=victory_h+draw_h+defeat_h
                    st.markdown("""
                        <style>
                        .metric-card {
                            background-color: #ffffff;
                            padding: 20px;
                            border-radius: 15px;
                            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                            border-left: 5px solid #4B90FF;
                            margin-bottom: 20px;
                        }
                        .metric-label {
                            font-size: 14px;
                            color: #6c757d;
                            font-weight: bold;
                            text-transform: uppercase;
                            margin-bottom: 5px;
                        }
                        .metric-value {
                            font-size: 32px;
                            font-weight: 900;
                            color: #1f1f1f;
                        }
                        .win { border-left-color: #28a745; }
                        .loss { border-left-color: #dc3545; }
                        .draw { border-left-color: #ffc107; }
                        </style>
                    """, unsafe_allow_html=True)

                    if matches != 0:
                        matches_h = victory_h + draw_h + defeat_h
                        matches_a = matches - matches_h
                        pts_total = (victory * 3) + draw
                        pts_h = (victory_h * 3) + draw_h
                        pts_a = (victory_a * 3) + draw_a
                  
                        avg_goal_h = round(goal_h / matches_h, 2) if matches_h > 0 else 0
                        avg_lost_h = round(goal_lost_h / matches_h, 2) if matches_h > 0 else 0
                        avg_goal_a = round(goal_a / matches_a, 2) if matches_a > 0 else 0
                        avg_lost_a = round(goal_lost_a / matches_a, 2) if matches_a > 0 else 0
                        avg_supp = int(int(supporter) / matches_h) if matches_h > 0 else 0

                        st.title("🏆 Analyse de Performance")
                        
                        col_a, col_b, col_c, col_d = st.columns(4)
                        
                        with col_a:
                            st.markdown(f'<div class="metric-card"><div class="metric-label">Matches</div><div class="metric-value">{matches}</div></div>', unsafe_allow_html=True)
                        with col_b:
                            st.markdown(f'<div class="metric-card"><div class="metric-label">Points/Match</div><div class="metric-value">{round(pts_total / matches, 2)}</div></div>', unsafe_allow_html=True)
                        with col_c:
                            st.markdown(f'<div class="metric-card"><div class="metric-label">Système préférentiel</div><div class="metric-value" style="font-size:24px">{system}</div></div>', unsafe_allow_html=True)
                        with col_d:
                            st.markdown(f'<div class="metric-card"><div class="metric-label">Buts Moy.</div><div class="metric-value">{round(goals / matches, 2)}</div></div>', unsafe_allow_html=True)

                        st.markdown("### 📊 Bilan des Résultats")
                        c1, c2, c3, c4 = st.columns(4)
                        c1.markdown(f'<div class="metric-card win"><div class="metric-label">Victoires</div><div class="metric-value" style="color:#28a745">{victory}</div></div>', unsafe_allow_html=True)
                        c2.markdown(f'<div class="metric-card draw"><div class="metric-label">Nuls</div><div class="metric-value" style="color:#ffc107">{draw}</div></div>', unsafe_allow_html=True)
                        c3.markdown(f'<div class="metric-card loss"><div class="metric-label">Défaites</div><div class="metric-value" style="color:#dc3545">{defeat}</div></div>', unsafe_allow_html=True)
                        c4.markdown(f'<div class="metric-card"><div class="metric-label">Total Points</div><div class="metric-value">{pts_total}</div></div>', unsafe_allow_html=True)

                        st.markdown("---")

                        st.markdown("""
                            <style>
                            .home-box { background-color: #f0f7ff; border-radius: 15px; padding: 20px; border: 1px solid #d1e3ff; }
                            .away-box { background-color: #fff5f5; border-radius: 15px; padding: 20px; border: 1px solid #ffd1d1; }
                            
                            /* Style pour les petites pastilles V N D */
                            .result-pill {
                                display: inline-block;
                                padding: 2px 10px;
                                border-radius: 20px;
                                font-size: 12px;
                                font-weight: bold;
                                color: white;
                                margin: 0 2px;
                            }
                            .pill-v { background-color: #28a745; }
                            .pill-n { background-color: #ffc107; color: #000; }
                            .pill-d { background-color: #dc3545; }

                            .stat-row {
                                display: flex;
                                justify-content: space-between;
                                padding: 8px 0;
                                border-bottom: 1px dashed #ccc;
                            }
                            .stat-label { font-weight: bold; color: #555; }
                            .stat-value { font-weight: 900; color: #1f1f1f; }
                            </style>
                        """, unsafe_allow_html=True)

                        col_left, col_right = st.columns(2)

                        with col_left:
                            st.markdown(f"""
                            <div class="home-box">
                                <h2 style="text-align:center; margin-bottom:5px;">🏠 DOMICILE</h2>
                                <div style="text-align:center; margin-bottom:10px;">
                                    <span style="font-size:40px; font-weight:900; color:#1f1f1f;">{round(pts_h / max(matches_h, 1), 2)}</span><br>
                                    <span style="color:#666; font-size:12px; font-weight:bold; text-transform:uppercase;">Points / Match</span>
                                </div>
                                <div style="text-align:center; margin-bottom:20px;">
                                    <span class="result-pill pill-v">{victory_h} V</span>
                                    <span class="result-pill pill-n">{draw_h} N</span>
                                    <span class="result-pill pill-d">{defeat_h} D</span>
                                </div>
                                <div class="stat-row"><span class="stat-label">👥 Supporters Moy.</span><span class="stat-value">{avg_supp}</span></div>
                                <div class="stat-row"><span class="stat-label">⚽ Buts Marqués</span><span class="stat-value">{goal_h} <small>({avg_goal_h}/m)</small></span></div>
                                <div class="stat-row"><span class="stat-label">🛡️ Buts Encaissés</span><span class="stat-value">{goal_lost_h} <small>({avg_lost_h}/m)</small></span></div>
                            </div>
                            """, unsafe_allow_html=True)

                        with col_right:
                            st.markdown(f"""
                            <div class="away-box">
                                <h2 style="text-align:center; margin-bottom:5px;">✈️ EXTÉRIEUR</h2>
                                <div style="text-align:center; margin-bottom:10px;">
                                    <span style="font-size:40px; font-weight:900; color:#1f1f1f;">{round(pts_a / max(matches_a, 1), 2)}</span><br>
                                    <span style="color:#666; font-size:12px; font-weight:bold; text-transform:uppercase;">Points / Match</span>
                                </div>
                                <div style="text-align:center; margin-bottom:20px;">
                                    <span class="result-pill pill-v">{victory_a} V</span>
                                    <span class="result-pill pill-n">{draw_a} N</span>
                                    <span class="result-pill pill-d">{defeat_a} D</span>
                                </div>
                                <div class="stat-row"><span class="stat-label">⚽ Buts Marqués</span><span class="stat-value">{goal_a} <small>({avg_goal_a}/m)</small></span></div>
                                <div class="stat-row"><span class="stat-label">🛡️ Buts Encaissés</span><span class="stat-value">{goal_lost_a} <small>({avg_lost_a}/m)</small></span></div>
                            </div>
                            """, unsafe_allow_html=True)


                        if state==True:
                                st.subheader("Évolution des points au cours la Saison")
                                st.line_chart(df_chart, x="Journée", y="Points Cumulés")
                        if mtc not in ["Korean Super Cup"]:
                            st.write("### Apparition de score:")
                            st.bar_chart(result,x="Score",y="apparition",color="Score")

                    st.divider()
            except Exception as e:
                st.info("Aucune data existante n'a été trouvé")
                st.error(e)#a cacher après
        return
    
    year_match=list(data_dict.keys())
    for i in year_match:
        matchs = data_dict.get(i) or data_dict.get(i, [])
        df_matchs = pd.DataFrame(matchs)
        Get_match_Year(df_matchs,i)
    
    st.markdown(f"### {selected_club} face aux autres équipes en championnat:")