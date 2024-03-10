from scraper import Scraper
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import os
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.StreamHandler()]
)


SAVE_DIR = "record_data"
TIMEOUT = 15
MAX_WORKERS = 10
print_lock = Lock()

if not os.path.exists(SAVE_DIR):
    logging.info("Creating directory for data.")
    os.makedirs(SAVE_DIR)


links = Scraper.scrape_map_links("https://web.archive.org/web/20080410031718/http://stats.climbing-soldiers.net/index.php")
links = ["https://web.archive.org/web/20080410031718/http://stats.climbing-soldiers.net/"+link for link in links]
with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = [executor.submit(Scraper.scrape(link, save_directory=SAVE_DIR, print_lock=print_lock)) for link in links]
    for future in as_completed(futures, timeout=TIMEOUT):
        pass
