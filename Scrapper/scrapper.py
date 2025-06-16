import pandas as pd
from io import BytesIO
import requests
from sqlalchemy import create_engine

DB_CONFIG = {
    'dbname': 'test_db',
    'user': 'admin',
    'password': 'root',
    'host': 'localhost',
    'port': '5432'
}

engine_url = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
engine = create_engine(engine_url)

response = requests.get("https://rbidocs.rbi.org.in/rdocs/content/docs/68774.xlsx")
response.raise_for_status()

excel_data = pd.read_excel(BytesIO(response.content), sheet_name=None) 

for sheet_name, df in excel_data.items():
    print(f"Inserting sheet '{sheet_name}' into table '{sheet_name}' ({len(df)} rows)")
    df.to_sql(sheet_name, engine, if_exists='replace', index=False)

print("All sheets inserted successfully.")
