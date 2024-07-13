import requests
from bs4 import BeautifulSoup
import pandas as pd
import urllib3
import sqlite3
import ssl
import numpy as np


ssl._create_default_https_context = ssl._create_unverified_context
import datetime 
# no of records i wanted to read from dataset.
no_of_records=100000
url = 'https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page'
r = requests.get(url, verify=False)
print('Response:', r)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
 

if r.status_code == 200:
  soup = BeautifulSoup(r.content, "html.parser")
else:
  print("you can't scrape data from this website")



id_of_year='faq2019'
d=soup.find(id=id_of_year)

all_links=[]
for link in d.find_all("a"):
  all_links.append(link.get('href'))

# feb links are from 3 to 6
feb_data=all_links[3:7]

# feb links are from 7 to 10
march_data=all_links[7:11]
feb_yellow_tripdata=pd.read_parquet(feb_data[0]).head(no_of_records)
feb_green_tripdata=pd.read_parquet(feb_data[1]).head(no_of_records)
feb_fhv_tripdata=pd.read_parquet(feb_data[2]).head(no_of_records)
feb_fhvhv_tripdata=pd.read_parquet(feb_data[3]).head(no_of_records)

march_yellow_tripdata=pd.read_parquet(march_data[0]).head(no_of_records)
march_green_tripdata=pd.read_parquet(march_data[1]).head(no_of_records)
march_fhv_tripdata=pd.read_parquet(march_data[2]).head(no_of_records)
march_fhvhv_tripdata=pd.read_parquet(march_data[3]).head(no_of_records)




month_tripdata = {
    "feb_yellow_tripdata": feb_yellow_tripdata,
    "feb_green_tripdata": feb_green_tripdata,
    "feb_fhv_tripdata": feb_fhv_tripdata,
    "feb_fhvhv_tripdata": feb_fhvhv_tripdata,
    "march_yellow_tripdata": march_yellow_tripdata,
    "march_green_tripdata": march_green_tripdata,
    "march_fhv_tripdata": march_fhv_tripdata,
    "march_fhvhv_tripdata": march_fhvhv_tripdata  
}



def clean_and_convert_df(df):
    for col in df.columns:
        if (pd.api.types.infer_dtype(df[col]) == 'object') or (pd.api.types.infer_dtype(df[col]) == 'category'):
            df[col] = df[col].astype(str)
            df[col] = df[col].str.replace(r'[^\x00-\x7F]+','', regex=True) 
        elif pd.api.types.is_datetime64_dtype(df[col]):
            df[col] = df[col].astype(str) # Convert to string directly
    
    # Replace any remaining NaN, NaT, or None values with "NULL"
    df = df.fillna('NULL')
    return df


# ... (your other code for establishing database connection etc.) ...
db_name = 'tripdata.db'
with sqlite3.connect(db_name) as conn:  
    cursor = conn.cursor()

    # Iterate through each DataFrame
    for key, value in month_tripdata.items():
        if isinstance(value, pd.DataFrame):
            # Get column names from the DataFrame
            column_names = value.columns.tolist()
            print(column_names)
            # Clean and convert dataframe values
            value = clean_and_convert_df(value)
            # value = value.replace({np.nan: None, pd.NaT: None})

            # Dynamically building column definitions with quoting for names and explicit data types 
            column_defs = []
            for col in column_names:
                sqlite_type = None
                col_type = pd.api.types.infer_dtype(value[col])
                if col_type == "object" or col_type == "string":
                    sqlite_type = "TEXT"
                elif col_type == "floating":
                    sqlite_type = "REAL"
                elif col_type == "integer":
                    sqlite_type = "INTEGER"
                elif col_type is None:  
                    sqlite_type = "NULL"
                column_defs.append(f'"{col}" {sqlite_type}') 
            
            create_table_query = f"CREATE TABLE IF NOT EXISTS {key} ({', '.join(column_defs)})"

            cursor.execute(create_table_query)  # Create the table (if not exists)

            # Convert DataFrame to a list of tuples (suitable for bulk insertion)
            data_tuples = [tuple(x) for x in value.to_numpy()]

            # Prepare the placeholder string for INSERT query
            placeholders = ','.join(['?'] * len(column_names))
            print(placeholders)
            # Insert data into the table
            cursor.executemany(f"INSERT INTO {key} VALUES ({placeholders})", data_tuples)
            print(key, "---> done")
        else:
            print(f"Skipping '{key}': Not a DataFrame")

    # Commit the changes to the database (important!)
    conn.commit()
