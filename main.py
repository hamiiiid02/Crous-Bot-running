from scraper import check_new_listings
import time
import warnings
import os
from telegram_bot import start_bot

from datetime import datetime


os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings("ignore")

print("bot started now !!!")

while True:
    current_datetime = datetime.now()
    current_time = current_datetime.strftime("%H:%M:%S")
    print("bot runned at :", current_time)
    try:
        check_new_listings()
    except Exception as e:
        print(f"Error: {e}")
    time.sleep(30)
