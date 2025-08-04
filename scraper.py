from db import init_db, get_all_logement_links, insert_logement, delete_missing_logements
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from telegram_bot import send_telegram_alert
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import InvalidSessionIdException, WebDriverException
import config
import time
from webdriver_manager.chrome import ChromeDriverManager

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

import subprocess
import re

def get_chromium_version():
    result = subprocess.run(["/usr/bin/chromium", "--version"], stdout=subprocess.PIPE)
    version_output = result.stdout.decode("utf-8")
    match = re.search(r"(\d+\.\d+\.\d+\.\d+)", version_output)
    return match.group(1) if match else None

def create_driver():
    options = Options()
    options.binary_location = "/usr/bin/chromium"

    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--remote-debugging-port=9222")

    chromium_version = get_chromium_version()
    if chromium_version:
        major_version = chromium_version.split('.')[0]
        service = Service(ChromeDriverManager(driver_version=major_version).install())
        return webdriver.Chrome(service=service, options=options)
    else:
        raise RuntimeError("Could not determine Chromium version")


def check_new_listings():
    driver = None
    try:
        driver = create_driver()
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
                        continue

                    name = listing.find_element(By.CSS_SELECTOR, "h3.fr-card__title a").text.strip()
                    address = listing.find_element(By.CSS_SELECTOR, "p.fr-card__desc").text.strip()
                    price = listing.find_element(By.CSS_SELECTOR, "ul.fr-badges-group li p.fr-badge").text.strip()

                    details = listing.find_elements(By.CSS_SELECTOR, "p.fr-card__detail")
                    area = "N/A"
                    for d in details:
                        if "m²" in d.text:
                            area = d.text.strip()
                            break

                    insert_logement(name, address, price, area, link)
                    send_telegram_alert(name, address, link)
                    print(f"✅ ADDED: {name} | {price} | {area} | {address} | {link}")

                except Exception as e:
                    print("⚠️ Error in listing:", e)
                    continue

            try:
                next_button = driver.find_element(By.CSS_SELECTOR, "a.fr-pagination__link--next")
                if next_button.get_attribute("aria-disabled") == "true":
                    print("✅ Last page reached.")
                    break
                driver.execute_script("arguments[0].click();", next_button)
                time.sleep(3)
                page += 1
            except Exception as e:
                print("❌ Couldn't find or click next button:", e)
                break

        delete_missing_logements(current_links)

    except InvalidSessionIdException:
        print("❌ Session expired. Restart the driver.")
        # Optionally retry here

    except WebDriverException as e:
        print("❌ WebDriver crashed or invalid:", e)

    except Exception as e:
        print("❌ General scraping error:", e)

    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass
