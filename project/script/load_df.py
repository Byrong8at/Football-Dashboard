import pandas as pd
import os
import ast
import re

def load_csv(name,base_dir):
    data_dir = os.path.join(base_dir, 'data')

    if not os.path.exists(data_dir):
            os.makedirs(data_dir)

    filename = os.path.join(data_dir, name)
    info = pd.read_csv(filename)
    return info

def clean_val(val):
    return int(val) if val.isdigit() else 0

def conv_val(val):
    try:
        if isinstance(val, str):
            # On remplace les '-' par '0' dans la chaîne AVANT de convertir pour éviter les bugs
            clean_raw = val.replace("'-'", "0").replace("-", "0")
            stats_dict = ast.literal_eval(clean_raw)
        else:
            stats_dict = val

        
    except Exception as e:
        stats_dict = {}
    return stats_dict

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

