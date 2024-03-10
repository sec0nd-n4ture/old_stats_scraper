from table_parser import *

class Scraper:
    @staticmethod
    def scrape(url: str, save_directory: str = ""):
        page = Fetcher.fetch(url)
        if not page:
            return False
        parser = Parser(page)
        if tables := parser.find_tables():
            if len(tables) > 1:
                record_table = tables[1]
                table_name = RecordTable.get_table_name(parser.find_table_heads()[1])
                records = RecordTable(record_table, table_name)
                records.save_json(save_directory)
                return True
        return False


    @staticmethod
    def scrape_map_links(url: str) -> dict[str, list[str, bool]]:
        '''Returns dictionary of map names, their links, and scrape status.'''
        page = Fetcher.fetch(url)
        parser = Parser(page)
        if tables := parser.find_tables():
            if len(tables) > 1:
                high_scores_table = tables[4]
                map_table = Table(high_scores_table)
                rows = map_table.table_rows
                links = [Table.get_table_cells(row)[0].find("a", href=True) for row in rows]
                return {link.contents[0] : [link["href"], False] for link in links}
