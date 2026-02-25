import pandas as pd
import os
import ast

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