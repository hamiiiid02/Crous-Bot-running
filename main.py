from scraper import check_new_listings
import time
import warnings
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings("ignore")

if __name__ == "__main__":
    while True:
        try:
            check_new_listings()
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(30)