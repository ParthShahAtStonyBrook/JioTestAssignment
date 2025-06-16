import pandas as pd
from io import BytesIO
from bs4 import BeautifulSoup
import requests
from sqlalchemy import create_engine
import regex as re

def fetch_url():
    url = 'https://www.rbi.org.in/scripts/neft.aspx'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    pattern = re.compile(
        r"List\s+of\s+NEFT\s+enabled\s+bank\s+branches\s+\(Consolidated\s+Indian\s+Financial\s+System\s+Code\).*",
        re.I,
    )

    excel_url = None

    for a in soup.find_all("a", href=True):
        full_text = " ".join(a.stripped_strings)
        if pattern.match(full_text):
            excel_url = a["href"]
            break
    return excel_url


DB_CONFIG = {
    'dbname': 'test_db',
    'user': 'admin',
    'password': 'root',
    'host': 'localhost',
    'port': '5432'
}

engine_url = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
engine = create_engine(engine_url)

excel_url = fetch_url()
print("Fetched current url : ", excel_url)
response = requests.get(excel_url)
response.raise_for_status()

excel_data = pd.read_excel(BytesIO(response.content), sheet_name=None) 

for sheet_name, df in excel_data.items():
    print(f"Inserting sheet '{sheet_name}' into table '{sheet_name}' ({len(df)} rows)")
    df.to_sql(sheet_name, engine, if_exists='replace', index=False)

print("All sheets inserted successfully.")
