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

def coord_import(datafile):
    data = pd.read_csv(datafile)
    metro_loc_data_load = data[['metro','lat','lng']]
    metro_loc_data = metro_loc_data_load.drop_duplicates()
    print(f"Successfully loaded {datafile}")
    return metro_loc_data
