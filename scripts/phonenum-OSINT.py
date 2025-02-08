import phonenumbers
from phonenumbers import geocoder, carrier, timezone, number_type, is_possible_number
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
import pycountry
from iso3166 import countries
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import pytz

def extract_max_phone_info(phone_number):
    try:
        # Parse the phone number
        parsed_number = phonenumbers.parse(phone_number)

        # Initialize results dictionary
        result = {}

        # Validity Check
        result["Valid"] = phonenumbers.is_valid_number(parsed_number)
        result["Possible Number"] = is_possible_number(parsed_number)

        # Basic Information (Country Code, National Number, Location, Carrier, Time Zones)
        result["Country Code"] = parsed_number.country_code
        result["National Number"] = parsed_number.national_number
        result["Location"] = geocoder.description_for_number(parsed_number, "en")
        result["Carrier"] = carrier.name_for_number(parsed_number, "en")
        result["Time Zones"] = list(timezone.time_zones_for_number(parsed_number))

        # Determine Line Type
        line_type = number_type(parsed_number)
        result["Line Type"] = line_type.name if hasattr(line_type, "name") else str(line_type)

        # Get the area code (first 3 digits)
        area_code = str(parsed_number.national_number)[:3]
        result["Area Code"] = area_code

        # Get Country Information using pycountry
        country_iso = phonenumbers.region_code_for_country_code(parsed_number.country_code)
        country = pycountry.countries.get(alpha_2=country_iso)
        if country:
            result["Country"] = country.name
            result["Country Alpha-2"] = country.alpha_2
            result["Country Alpha-3"] = country.alpha_3
            result["Country Numeric"] = country.numeric

        # Geolocation info based on location string
        if result["Location"]:
            geolocator = Nominatim(user_agent="phone_geolocator")
            location = geolocator.geocode(result["Location"])
            if location:
                tf = TimezoneFinder()
                precise_timezone = tf.timezone_at(lat=location.latitude, lng=location.longitude)
                result["Precise Time Zone"] = precise_timezone
                result["Coordinates"] = {
                    "Latitude": location.latitude,
                    "Longitude": location.longitude
                }

                # Reverse geocoding for detailed address info
                reverse_location = geolocator.reverse((location.latitude, location.longitude), language='en', exactly_one=True)
                if reverse_location:
                    address = reverse_location.raw.get('address', {})
                    result["Address"] = {
                        "City": address.get('city', address.get('town', 'City not found')),
                        "County/District": address.get('county', 'County not found'),
                        "State": address.get('state', 'State not found'),
                        "Country": address.get('country', 'Country not found'),
                        "Postcode": address.get('postcode', 'Postcode not found'),
                        "Full Address": reverse_location.address
                    }

                # Calculate timezone offset
                if precise_timezone:
                    timezone_obj = pytz.timezone(precise_timezone)
                    utc_offset = datetime.now(timezone_obj).utcoffset().total_seconds() / 3600
                    result["UTC Offset"] = f"UTC{utc_offset:+.1f}"

        # ISO3166 Metadata (Country Data)
        if country_iso in countries:
            iso_country = countries.get(country_iso)
            result["ISO3166 Metadata"] = {
                "Name": iso_country.name,
                "Alpha-2": iso_country.alpha2,
                "Alpha-3": iso_country.alpha3,
                "Numeric": iso_country.numeric
            }

        # Scrape additional information (if needed, include logic for scraping public sites)
        additional_info = scrape_phone_info(phone_number)
        if additional_info:
            result["Scraped Data"] = additional_info

        return result

    except phonenumbers.NumberParseException as e:
        return {"Error": f"Invalid phone number: {e}"}
    except Exception as e:
        return {"Error": str(e)}

def scrape_phone_info(phone_number):
    """
    Scrape additional information about the phone number from public websites.
    Returns a dictionary of additional phone info.
    """
    info = {}

    try:
        # List of websites to scrape from
        websites = [
            f"https://www.numberguru.com/phone/{phone_number}/",   # NumberGuru
            f"https://www.truecaller.com/search/{phone_number}",  # TrueCaller
            f"https://www.whitepages.com/phone/{phone_number}",   # WhitePages
            f"https://www.spokeo.com/phone/{phone_number}",       # Spokeo
        ]

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        }

        # Try scraping from all websites
        for url in websites:
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Extract info from the page (adjust based on actual page structure)
                if "numberguru" in url:
                    location = soup.find('span', {'class': 'location'})
                    if location:
                        info["NumberGuru Location"] = location.get_text(strip=True)

                elif "truecaller" in url:
                    name = soup.find('h2', {'class': 'name'})
                    if name:
                        info["TrueCaller Name"] = name.get_text(strip=True)

                elif "whitepages" in url:
                    address = soup.find('div', {'class': 'address'})
                    if address:
                        info["WhitePages Address"] = address.get_text(strip=True)

                elif "spokeo" in url:
                    location = soup.find('div', {'class': 'location'})
                    if location:
                        info["Spokeo Location"] = location.get_text(strip=True)

    except Exception as e:
        info["Scraped Error"] = str(e)

    return info

def phone_number_lookup(phone_number):
    info = extract_max_phone_info(phone_number)

    # Print the results as JSON
    import json
    print(json.dumps(info, indent=4))

if __name__ == "__main__":
    print("WARNING: THIS TOOL GETS LOTS OF THINGS WRONG, PLEASE VERIFY EVERYTHING THAT HAS BEEN GIVEN IN THIS TOOL!")
    print("\n")
    phone_number = input("Enter the phone number (including the country code, e.g., +14155552671): ")
    phone_number_lookup(phone_number)
