import os
import json
import sqlite3


json_folder = 'record_data'
db_file = 'data.db'

conn = sqlite3.connect(db_file)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    time REAL,
    date REAL
)
''')


for json_file in os.listdir(json_folder):
    if json_file.endswith('.json'):
        file_path = os.path.join(json_folder, json_file)
        
        with open(file_path, 'r') as file:
            data = json.load(file)
        
        for entry in data:
            for value in entry.values():
                name = value['name']
                time = value['time']
                date = value['date']
                
                cursor.execute('''
                    INSERT INTO records (name, time, date)
                    VALUES (?, ?, ?)
                ''', (name, time, date))

conn.commit()
conn.close()

print("Data inserted successfully from all files.")
