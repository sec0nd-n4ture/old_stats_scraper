import os
import sqlite3
import json


class TimeConverter:
    @staticmethod
    def convert_time_to_tdatetime(time_str):
        minutes, seconds = map(int, time_str.split(":"))
        tdatetime_fraction = (minutes * 60 + seconds) / 86400
        return tdatetime_fraction


class DatabaseManager:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            time REAL,
            date REAL,
            map TEXT
        )
        ''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS maps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
        ''')

    def close(self):
        self.conn.commit()
        self.conn.close()


class MapManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def create_map(self, map_name):
        self.db_manager.cursor.execute('SELECT id FROM maps WHERE name = ?', (map_name,))
        result = self.db_manager.cursor.fetchone()
        
        if result:
            return result[0]
        else:
            self.db_manager.cursor.execute('INSERT INTO maps (name) VALUES (?)', (map_name,))
            return self.db_manager.cursor.lastrowid


class RecordInserter:
    def __init__(self, db_manager, map_manager):
        self.db_manager = db_manager
        self.map_manager = map_manager

    def insert_stats(self, json_folder):
        for json_file in os.listdir(json_folder):
            if json_file.endswith('.json'):
                file_path = os.path.join(json_folder, json_file)
                map_name = os.path.splitext(json_file)[0]

                self.map_manager.create_map(map_name)

                with open(file_path, 'r') as file:
                    data = json.load(file)

                for entry in data:
                    for value in entry.values():
                        name = value['name']
                        time = TimeConverter.convert_time_to_tdatetime(value['time'])
                        date = value['date']
                        
                        self.db_manager.cursor.execute('''
                            INSERT INTO records (name, time, date, map)
                            VALUES (?, ?, ?, ?)
                        ''', (name, time, date, map_name))


db_file = 'data.db'
db_manager = DatabaseManager(db_file)
map_manager = MapManager(db_manager)
json_folder = 'record_data'
record_inserter = RecordInserter(db_manager, map_manager)
record_inserter.insert_stats(json_folder)
db_manager.close()


print("Data inserted successfully.")
