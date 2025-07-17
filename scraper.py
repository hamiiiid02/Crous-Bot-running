from db import init_db, get_all_logement_links, insert_logement, delete_missing_logements
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from telegram_bot import send_telegram_alert
from selenium.webdriver.chrome.service import Service
import config
import time
from webdriver_manager.chrome import ChromeDriverManager  # ✅ new

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--log-level=3")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

TARGET_RESIDENCES = [
    "CITE INTERNATIONALE", "CITE LUMINY", "CITE GALINAT", "RESIDENCE LES DOUANES",
    "GASTON BERGER", "RESIDENCE ALICE CHATENOUD", "RESIDENCE ARC DE MEYRAN",
    "RESIDENCE ROCHER DES DOMS", "RESIDENCE LES BALUSTRES", "RESIDENCE LUCIEN CORNIL",
    "RESIDENCE SYLVABELLE", "RESIDENCE LES PETITES MARIES MARSEILLE 1",
    "RESIDENCE OPALE", "RESIDENCE MADAGASCAR", "RESIDENCE LI PASSEROUN AIX",
    "CITE UNIVERSITAIRE CUQUES AIX", "CLAUDE DELORME"
]

def is_target_residence(label):
    label_normalized = label.strip().upper()
    return any(residence in label_normalized for residence in TARGET_RESIDENCES)

    

def check_new_listings():
    init_db()
    existing_links = get_all_logement_links()
    current_links = set()

    driver.get(config.SCRAPE_URL)
    time.sleep(3)

    page = 1
    while True:
        print(f"\n🟦 Scraping Page {page}")
        listings = driver.find_elements(By.CSS_SELECTOR, "div.fr-card")
        print("Found", len(listings), "listings")

        for listing in listings:
            try:
                link = listing.find_element(By.CSS_SELECTOR, "h3.fr-card__title a").get_attribute("href").strip()
                current_links.add(link)

                if link in existing_links:
                    continue  # Already exists

                name = listing.find_element(By.CSS_SELECTOR, "h3.fr-card__title a").text.strip()
                address = listing.find_element(By.CSS_SELECTOR, "p.fr-card__desc").text.strip()
                price = listing.find_element(By.CSS_SELECTOR, "ul.fr-badges-group li p.fr-badge").text.strip()

                details = listing.find_elements(By.CSS_SELECTOR, "p.fr-card__detail")
                area = "N/A"
                for d in details:
                    if "m²" in d.text:
                        area = d.text.strip()
                        break

                if not is_target_residence(name):
                    insert_logement(name, address, price, area, link)
                    send_telegram_alert(name, address, link)
                    print(f"✅ MATCHED: {name} | {price} | {area} | {address} | {link}")
                else:
                    print(f"❌ Skipped: {name}")


            except Exception as e:
                print("⚠️ Error:", e)
                continue

        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "a.fr-pagination__link--next")
            aria_disabled = next_button.get_attribute("aria-disabled")
            if aria_disabled == "true":
                print("✅ Last page reached.")
                break
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(3)
            page += 1
        except Exception as e:
            print("❌ Couldn't find or click next button:", e)
            break

    delete_missing_logements(current_links)
