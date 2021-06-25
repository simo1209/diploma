import psycopg2
import pandas as pd
from backoffice import bcrypt

thousand_names = pd.read_csv("./baby-names.csv", nrows=100, usecols=['name'])
familly_names = thousand_names.copy()

conn = psycopg2.connect("dbname=qrpayment user=simo")
cur = conn.cursor()

for index1, row1 in thousand_names.iterrows():
    for index2, row2 in familly_names.iterrows():
        first_name = row1['name']
        last_name = row2['name']
        cur.execute("INSERT INTO accounts(first_name, last_name, email, password, phone, address_id, \"UCN\", company_id) VALUES (%s, %s, %s, %s, '1234567890', 2, '1234567890', null);",
        (first_name, last_name, first_name+last_name+'@example.com',bcrypt.generate_password_hash(first_name+last_name, 12).decode('utf-8'),))
        print(first_name, last_name)
    conn.commit()


cur.close()
conn.close()


