from table_parser import *


class Scraper:
    @staticmethod
    def scrape(url: str, save_directory: str = "", print_lock=None):
        page = Fetcher.fetch(url)
        if not page:
            print(f"Skipping {url}")
            return False
        parser = Parser(page)
        if tables := parser.find_tables():
            if len(tables) > 1:
                record_table = tables[1]
                table_name = RecordTable.get_table_name(parser.find_table_heads()[1])
                records = RecordTable(record_table, table_name)
                records.save_json(save_directory)
                if print_lock:
                    with print_lock:
                        print(f"Scraped and saved {url}")
                return True


    @staticmethod
    def scrape_map_links(url: str) -> list[str]:
        page = Fetcher.fetch(url)
        parser = Parser(page)
        if tables := parser.find_tables():
            if len(tables) > 1:
                high_scores_table = tables[4]
                map_table = Table(high_scores_table)
                rows = map_table.table_rows
                return [Table.get_table_cells(row)[0].find("a", href=True)["href"] for row in rows]
