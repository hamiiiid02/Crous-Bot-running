from telegram import Bot
import config
import re
import requests

bot = Bot(token=config.TELEGRAM_BOT_TOKEN)

def extract_entity(address):
    address = address.strip()

    # Case 1: ends with word + number (e.g., Cedex 4, Bloc A 3000)
    match = re.search(r'([\wÀ-ÿ\'\- ]+\d+)$', address)
    if match:
        return match.group(1).strip()

    # Case 2: ends with number(s) then city name (e.g., 30000 Nîmes)
    match = re.search(r'\d+\s+([\wÀ-ÿ\'\-]+)$', address)
    if match:
        return match.group(1).strip()

    # Case 3: just return last word
    return address.split()[-1] if address else "N/A"

def send_telegram_alert(name, address, link):
    entity = extract_entity(address)

    message = (
        f"🏙️ *Entity:* {entity}\n"
        f"🏷️ *Label:* {name}\n"
        f"📍 *Address:* {address}\n"
        f"🔗 [Link]({link})"
    )

    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': config.TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }

    response = requests.post(url, data=payload)
    if response.status_code != 200:
        print("❌ Telegram error:", response.text)

def start_bot():

    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': config.TELEGRAM_CHAT_ID,
        'text': "boot started",
        'parse_mode': 'Markdown'
    }

    response = requests.post(url, data=payload)
    if response.status_code != 200:
        print("❌ Telegram error:", response.text)
