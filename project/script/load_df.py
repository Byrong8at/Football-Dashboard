import pandas as pd
import os
import ast
import re
import glob
import streamlit as st
import plotly.express as px


def load_all_csv(base_dir):
    data_dir = os.path.join(base_dir, 'data')

    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # Recherche tous les fichiers qui matchent "Clubs_*.csv"
    all_files = glob.glob(os.path.join(data_dir, "Clubs_*.csv"))
    
    df_list = []
    for filename in all_files:
        try:
            df = pd.read_csv(filename)
            df_list.append(df)
        except Exception as e:
            print(f"Erreur lors de la lecture de {filename}: {e}")
            
    if df_list:
        return pd.concat(df_list, ignore_index=True)
    else:
        return pd.DataFrame()

def clean_val(val):
    return int(val) if str(val).isdigit() else 0

def conv_val(val):
    try:
        if isinstance(val, str):
            # On remplace UNIQUEMENT la valeur "-" exacte (avec ses guillemets simples ou doubles) par "0"
            # Cela protège les dates "2024-05-01" et les scores non joués "-:-"
            clean_raw = val.replace("'-'", "'0'")
            clean_raw = clean_raw.replace('"-"', '"0"')
            
            parsed = ast.literal_eval(clean_raw)
        else:
            parsed = val
    except Exception as e:
        parsed = []
    return parsed

def style_df(df):
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

    def apply_row_style(row):
        styles = [''] * len(row)
        
        score = str(row['Score'])
        lieu = row['Lieu']
        
        if score != "-:-" and ":" in score:
            try:
                parties = score.split(':')                    
                score_home = int(re.search(r'\d+', parties[0]).group())
                score_away = int(re.search(r'\d+', parties[1]).group())

                if score_home == score_away:
                    bg_color = 'background-color: #fff3cd;' # Jaune (Nul)
                elif (lieu == 'H' and score_home > score_away) or (lieu == 'A' and score_away > score_home):
                    bg_color = 'background-color: #d4edda;' # Vert (Victoire)
                else:
                    bg_color = 'background-color: #f8d7da;' # Rouge (Défaite)
                
                # On applique cette couleur de fond à toute la ligne
                styles = [bg_color] * len(row)
            except:
                pass

        # 2. STYLES SPÉCIFIQUES PAR COLONNE (écrasent la couleur de ligne si besoin)
        idx_lieu = df.columns.get_loc("Lieu")
        if lieu == 'H':
            styles[idx_lieu] += 'color: #0f5132; font-weight: bold; border-right: 1px solid #ccc;'
        elif lieu == 'A':
            styles[idx_lieu] += 'color: #842029; font-weight: bold; border-right: 1px solid #ccc;'

        return styles

    return df.style.apply(apply_row_style, axis=1) \
        .set_properties(subset=['Journée'], **{
            'background-color': '#e9ecef', 
            'color': 'black', 
            'font-weight': 'bold',
            'text-align': 'center'
        }) \
        .set_properties(subset=['Adversaire'], **{'font-weight': 'bold'}) \
        .set_properties(subset=['Score'], **{'font-weight': 'bold', 'text-align': 'center'})

def Get_All_Match(y_,df_Club,selected_club):
        club_y=df_Club[(df_Club["Year"] == (y_)) & (df_Club["Club"] == selected_club)]#probleme la ligue de ctte année, donc manque deux équipe en plus
        if club_y.empty:
            return st.info(f"Aucune donnée de ligue trouvée pour {selected_club} en {y_}.")
        nom_ligue = club_y['League'].iloc[0]
        filter_league = df_Club[(df_Club["Year"] == (y_)) & (df_Club["League"] == nom_ligue)]

        
        data_graph = []

        for _, row in filter_league.iterrows():
            club_name = row['Club']
            icon_url = row['Team_Icon']
            
            matchs_list = conv_val(row['Match_Stat'])
            
            pts_h = 0
            matchs_h = 0
            pts_a = 0
            matchs_a = 0
            
            for m in matchs_list:
                if isinstance(m, str):#Manage error (Yogjin)
                    continue
                if m.get('Type') == nom_ligue:
                    score = str(m.get('Score', '')).strip()
                    lieu = m.get('Venue') or m.get('Lieu', 'H')
                    
                    if score != "-:-" and ":" in score:
                        try:
                            parties = score.split(':')                    
                            score_home = int(re.search(r'\d+', parties[0]).group())
                            score_away = int(re.search(r'\d+', parties[1]).group())
                            
                            if lieu == "H":
                                matchs_h += 1
                                if score_home > score_away: pts_h += 3
                                elif score_home == score_away: pts_h += 1
                            elif lieu == "A":
                                matchs_a += 1
                                if score_away > score_home: pts_a += 3
                                elif score_home == score_away: pts_a += 1
                        except Exception:
                            pass
            
            avg_pts_h = round(pts_h / matchs_h, 2) if matchs_h > 0 else 0
            avg_pts_a = round(pts_a / matchs_a, 2) if matchs_a > 0 else 0
            
            if matchs_h > 0 or matchs_a > 0:
                data_graph.append({
                    "Club": club_name,
                    "Pts Domicile": avg_pts_h,
                    "Pts Extérieur": avg_pts_a,
                    "Icon": icon_url
                })
                
        if data_graph:
                df_graph = pd.DataFrame(data_graph)
                
                mediane_h = df_graph['Pts Domicile'].median()
                mediane_a = df_graph['Pts Extérieur'].median()
                
                x_min, x_max = df_graph['Pts Domicile'].min() - 0.4, df_graph['Pts Domicile'].max() + 0.4
                y_min, y_max = df_graph['Pts Extérieur'].min() - 0.4, df_graph['Pts Extérieur'].max() + 0.4

                fig_quadrant = px.scatter(
                    df_graph, 
                    x="Pts Domicile", 
                    y="Pts Extérieur", 
                    title=f"Performance Domicile vs Extérieur ({nom_ligue} - {y_+1})"
                )
                
                for i, row in df_graph.iterrows():
                    fig_quadrant.add_layout_image(
                        dict(
                            source=row['Icon'],
                            xref="x",
                            yref="y",
                            x=row['Pts Domicile'],
                            y=row['Pts Extérieur'],
                            sizex=0.17, 
                            sizey=0.17, 
                            xanchor="center",
                            yanchor="middle",
                        )
                    )
                
                fig_quadrant.add_hline(y=mediane_a, line_dash="dot", line_color="#bfbfbf", line_width=1, annotation_text="Médiane Ligue Ext.", annotation_position="bottom right")
                fig_quadrant.add_vline(x=mediane_h, line_dash="dot", line_color="#bfbfbf", line_width=1, annotation_text="Médiane Ligue Dom.", annotation_position="top left")
                
                # Top-Right: High Home, High Away (Green zone) - "Performant Partout"
                fig_quadrant.add_shape(type="rect", xref="x", yref="y", x0=mediane_h, y0=mediane_a, x1=x_max, y1=y_max, fillcolor="#d1e7dd", opacity=0.3, line_width=0, layer="below")
                
                # Bottom-Left: Low Home, Low Away (Red zone) - "Difficultés Partout"
                fig_quadrant.add_shape(type="rect", xref="x", yref="y", x0=x_min, y0=y_min, x1=mediane_h, y1=mediane_a, fillcolor="#f8d7da", opacity=0.3, line_width=0, layer="below")
                
                # Bottom-Right: High Home, Low Away (Blue zone) - "Fort à Domicile"
                fig_quadrant.add_shape(type="rect", xref="x", yref="y", x0=mediane_h, y0=y_min, x1=x_max, y1=mediane_a, fillcolor="#cfe2f3", opacity=0.3, line_width=0, layer="below")
                
                # Top-Left: Low Home, High Away (Orange zone) - "Fort à l'Extérieur"
                fig_quadrant.add_shape(type="rect", xref="x", yref="y", x0=x_min, y0=mediane_a, x1=mediane_h, y1=y_max, fillcolor="#fff3cd", opacity=0.3, line_width=0, layer="below")
                
                fig_quadrant.update_layout(
                    xaxis_title="Points par Match Moy(Domicile)",
                    yaxis_title="Points par Match Moy(Extérieur)",
                    height=650,
                    showlegend=False,
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    margin=dict(l=30, r=30, t=60, b=30)
                )
                
                st.plotly_chart(fig_quadrant)
                
        else:
                st.info(f"Pas assez de données pour générer le graphique en {y_}.")

