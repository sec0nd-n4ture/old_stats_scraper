from scraper import Scraper
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock, Thread
import os
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.StreamHandler()]
)


SAVE_DIR = "record_data"
TIMEOUT = 15
MAX_WORKERS = 10
links_lock = Lock()
USE_THREAD_POOL = False
rate_limited = False
fired_threads = 0
RATE_LIMIT_WAIT_SECONDS = 200


if not os.path.exists(SAVE_DIR):
    logging.info("Creating directory for data.")
    os.makedirs(SAVE_DIR)


class ScraperThread:
    def __init__(self, url, save_directory, map_name) -> None:
        self.url = url
        self.save_directory = save_directory
        self.map_name = map_name
        self.retries = 0
        self.status = False
        self.thread = None

    def run(self) -> None:
        global rate_limited
        if rate_limited:
            return
        self.retries += 1
        try:
            scrape_result = Scraper.scrape(self.url, self.save_directory)
            logging.info(f"Scraped and saved {self.map_name}")
        except:
            scrape_result = False
            logging.info(f"Failed to fetch data for {self.map_name}")
        if not scrape_result and self.retries >= 3:
            # give up after 3 retries
            scrape_result = True
        self.status = scrape_result
        if not scrape_result:
            rate_limited = True

    def start(self):
        self.thread = Thread(target=self.run, daemon=True)
        self.thread.start()
try:
    links = Scraper.scrape_map_links("https://web.archive.org/web/20080410031718/http://stats.climbing-soldiers.net/index.php")
except:
    logging.fatal("Failed to fetch links, quitting.")
    exit(1)
logging.info("Fetched links.")
for key in links:
    links[key][0] = "https://web.archive.org/web/20080410031718/http://stats.climbing-soldiers.net/" + links[key][0]

if USE_THREAD_POOL:
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(Scraper.scrape(links[key][0], save_directory=SAVE_DIR)) for key in links]
        for future in as_completed(futures, timeout=TIMEOUT):
            pass
else:
    logging.info("Creating threads.")
    threads = [ScraperThread(links[key][0], SAVE_DIR, key) for key in links]
    logging.info("Starting threads...")
    while not all([thread.status for thread in threads]):
        for thread in threads:
            if rate_limited:
                break
            if not thread.status:
                thread.start()
                fired_threads += 1
            if fired_threads >= MAX_WORKERS:
                time.sleep(TIMEOUT)
                fired_threads = 0
        logging.info(f"Rate limited, waiting {RATE_LIMIT_WAIT_SECONDS} seconds...")
        logging.info(f"Status: {sum([x.status for x in threads])} done out of {len(threads)}")
        time.sleep(RATE_LIMIT_WAIT_SECONDS)
        rate_limited = False
    logging.info("Completed.")
