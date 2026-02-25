import pandas as pd
import os

def load_csv(name,base_dir):
    data_dir = os.path.join(base_dir, 'data')

    if not os.path.exists(data_dir):
            os.makedirs(data_dir)

    filename = os.path.join(data_dir, name)
    info = pd.read_csv(filename)
    return info

def clean_val(val):
    return int(val) if val.isdigit() else 0
