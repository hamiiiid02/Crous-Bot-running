from scraper import check_new_listings
import time
import warnings
import os
from telegram_bot import start_bot



os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings("ignore")

if __name__ == "__main__":
    start_bot()
    while True:
        try:
            check_new_listings()
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(30)