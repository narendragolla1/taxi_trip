
import requests

from bs4 import BeautifulSoup
import pandas as pd
import urllib3
import sqlite3
import ssl
ssl._create_default_https_context = ssl._create_unverified_context


 

# no of records i wanted to read from dataset.
no_of_records=100000
url = 'https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page'
r = requests.get(url, verify=False)
print('Response:', r)
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
 

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

db_name='tripdata.db'

conn = sqlite3.connect(db_name)

for key, value in month_tripdata.items():
  # Check if value is a DataFrame (assuming DataFrames in the dictionary)
  if isinstance(value, pd.DataFrame):
    cursor = conn.cursor()

    # Get column names from the DataFrame
    column_names = value.columns.tolist()

    # Convert column names and data types to a comma-separated string for SQL
    column_defs = ', '.join([f"{col} {pd.api.types.infer_dtype(value[col])}" for col in column_names])

    # Create the table query
    create_table_query = f"""CREATE TABLE IF NOT EXISTS {key} ({column_defs});"""

    # Execute the query to create the table
    conn.execute(create_table_query)

    # Convert DataFrame to a list of tuples (suitable for bulk insertion)
    data_tuples = value.to_records(index=False)

    # Prepare the placeholder string for INSERT query
    placeholders = ','.join(['?'] * len(column_names))

    # Insert data into the table
    conn.executemany(f"INSERT INTO {key} VALUES ({placeholders})", data_tuples)
    print(i,"---> done,")
  else:
    print(f"Skipping '{key}': Not a DataFrame")

conn.commit()
conn.close()

