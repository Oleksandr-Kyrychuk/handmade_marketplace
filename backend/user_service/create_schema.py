# create_schema.py
import os
import psycopg2

db_url = os.environ["DATABASE_URL"].replace("&channel_binding=require", "")
conn = psycopg2.connect(db_url)
conn.autocommit = True
cur = conn.cursor()
# cur.execute("CREATE SCHEMA IF NOT EXISTS users_schema; GRANT ALL ON SCHEMA users_schema TO dev;")
cur.execute("CREATE SCHEMA IF NOT EXISTS users_schema;")
cur.close()
conn.close()
print("Schema created successfully!")
