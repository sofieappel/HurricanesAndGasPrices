# import to data frame
import pandas as pd

def df_import(datafile):
    try:
        pri_data = pd.read_csv(datafile)
        print(f"Successfully loaded {datafile}")
    except Exception as e:
        
        try: 
            pri_data = pd.read_csv(datafile, low_memory = False)
            print(f"Successfully loaded {datafile}")

        except Exception as e:
            print(f"Error loading primary file{e}")
            return None

    return pri_data