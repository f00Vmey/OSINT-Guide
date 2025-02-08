import requests
from bs4 import BeautifulSoup
import re
import whois
import json
import csv
import shodan
import pandas as pd

# === USER INPUT ===
TARGET_URL = input("Enter the target URL: ")
SHODAN_API_KEY = input("Enter your Shodan API Key: ")
USE_HIBP = input("Do you want to use HaveIBeenPwned? (yes/no): ").strip().lower() == "yes"
HIBP_API_KEY = input("Enter your HaveIBeenPwned API Key: ") if USE_HIBP else None
OUTPUT_JSON = "osint_results.json"
OUTPUT_CSV = "osint_results.csv"

# === DATA STORAGE ===
results = {
    "emails": [],
    "social_media": [],
    "metadata": {},
    "whois": {},
    "shodan": {},
    "hibp": {},
}

# === FUNCTION TO SCRAPE WEBSITE ===
def scrape_website(url):
    print(f"[+] Scraping: {url}")
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract emails
        emails = set(re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", soup.text))
        results["emails"].extend(emails)

        # Extract social media links
        social_patterns = {"facebook": "facebook.com", "twitter": "twitter.com", "linkedin": "linkedin.com"}
        for link in soup.find_all("a", href=True):
            for platform, pattern in social_patterns.items():
                if pattern in link["href"]:
                    results["social_media"].append({"platform": platform, "url": link["href"]})

        # Extract metadata
        results["metadata"]["title"] = soup.title.string if soup.title else "N/A"
        meta_desc = soup.find("meta", attrs={"name": "description"})
        results["metadata"]["description"] = meta_desc["content"] if meta_desc else "N/A"
    except Exception as e:
        print(f"[!] Error scraping {url}: {e}")

# === WHOIS LOOKUP ===
def get_whois(domain):
    print(f"[+] Performing WHOIS lookup on {domain}")
    try:
        whois_data = whois.whois(domain)
        results["whois"] = {
            "registrar": whois_data.registrar,
            "creation_date": whois_data.creation_date,
            "expiration_date": whois_data.expiration_date,
            "name_servers": whois_data.name_servers,
        }
    except Exception as e:
        print(f"[!] WHOIS lookup failed: {e}")

# === SHODAN SCAN ===
def get_shodan_data(ip):
    print(f"[+] Performing Shodan scan on {ip}")
    try:
        api = shodan.Shodan(SHODAN_API_KEY)
        shodan_data = api.host(ip)
        results["shodan"] = {
            "organization": shodan_data.get("org", "N/A"),
            "os": shodan_data.get("os", "N/A"),
            "ports": shodan_data.get("ports", []),
            "vulnerabilities": shodan_data.get("vulns", []),
        }
    except Exception as e:
        print(f"[!] Shodan scan failed: {e}")

# === EXPORT RESULTS ===
def save_results():
    # Save as JSON
    with open(OUTPUT_JSON, "w") as json_file:
        json.dump(results, json_file, indent=4)
    print(f"[+] Results saved to {OUTPUT_JSON}")

    # Save as CSV
    df = pd.DataFrame.from_dict(results, orient='index')
    df.to_csv(OUTPUT_CSV)
    print(f"[+] Results saved to {OUTPUT_CSV}")

# === MAIN EXECUTION ===
if __name__ == "__main__":
    scrape_website(TARGET_URL)
    get_whois(TARGET_URL.replace("https://", "").replace("http://", ""))
    save_results()
    print("[+] OSINT Scan Completed!")
