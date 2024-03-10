from bs4 import BeautifulSoup, Tag, NavigableString
import requests
import json


class Table:
    def __init__(self, table: Tag | NavigableString) -> None:
        self.table = table

    @property
    def table_body(self):
        return self.table.find("tbody")
    
    @property
    def table_rows(self):
        return self.table_body.find_all("tr")
    
    @staticmethod
    def get_table_cells(row: Tag | NavigableString):
        return row.find_all("td")


class RecordTable(Table):
    def __init__(self, table: Tag | NavigableString, table_name: str) -> None:
        super().__init__(table)
        self.table_name = table_name
    
    def get_records(self):
        rows = self.table_rows
        return [{Table.get_table_cells(row)[0].contents[0]: 
                    {
                        "name": Table.get_table_cells(row)[1].find("a").contents[0],
                        "time": Table.get_table_cells(row)[3].contents[0],
                        "date": Table.get_table_cells(row)[4].contents[0]
                    }
                } for row in rows]

    def save_json(self, save_directory: str = ""):
        with open(save_directory + "/" + self.table_name + ".json", "w") as fd:
            json.dump(self.get_records(), fd, indent=2)

    # this gets the map name
    @staticmethod
    def get_table_name(table_head: Tag | NavigableString):
        return table_head.find("h1").contents[0].split("'")[0]

class Parser:
    def __init__(self, page: str) -> None:
        self.page = page
        self.soup = BeautifulSoup(self.page, features="html.parser")
    
    def find_tables(self) -> list[Tag|NavigableString]:
        tables_navstr = self.soup.find_all("table", class_="borderB")
        return tables_navstr
    
    def find_table_heads(self) -> list[Tag|NavigableString]:
        table_heads_navstr = self.soup.find_all("div", class_="tableHead")
        return table_heads_navstr

class Fetcher:
    @staticmethod
    def fetch(url: str):
        try:
            response = requests.get(url)
            return response.text
        except requests.exceptions.RequestException as e:
            print(repr(e))


class Record:
    def __init__(self,
                 rank: int, 
                 name: str,
                 time: str,
                 date: str) -> None:
        self.rank = rank
        self.name = name
        self.time = time
        self.date = date

    def __str__(self) -> str:
        return f"Rank: {self.rank}, Name: {self.name}, Time: {self.time}, Date: {self.date}"

    @classmethod
    def from_dict(cls, record_dict: dict):
        return cls(list(record_dict.keys())[0],
                    *(record_dict[list(record_dict.keys())[0]][key] for key in record_dict[list(record_dict.keys())[0]].keys()))
