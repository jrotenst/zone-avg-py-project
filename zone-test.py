import json

from googleapiclient.discovery import build
from google.oauth2 import service_account

CREDENTIALS_FILE = "credentials.json"

# Define scope
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Authenticate
creds = service_account.Credentials.from_service_account_file(
    CREDENTIALS_FILE, scopes=SCOPES
)

# Connect to Sheets API
service = build("sheets", "v4", credentials=creds)

SPREADSHEET_ID = "1omGaFtd-J1BknRiOLvO6Z8LqrblRUQPX8wHyvHVeyOc"
LISTINGS_FILE = "listings.json"
LISTINGS = json.load(open(LISTINGS_FILE, "r")).get("rows", [])

def get_sheet_rows():

    print("Getting sheet rows...")

    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="Zones!A2:F14"
    ).execute()

    return result.get("values", [])

def get_avg_price(row):
    name = row[0]
    sections = row[1].split(",")
    exact_sections = row[2] == "Y"
    count = int(row[5])

    # Find matching listings for row (zone)
    matching_listings = list(filter(lambda listing: is_matching_listing(listing, sections, exact_sections), LISTINGS))

    # Sort listings by price ascending and slice by count
    cheapest_listings = matching_listings.sort(key=lambda listing: listing["price"])[:count]

    # Return sum of all prices divided by count
    return sum(map(lambda listing: listing["price"], cheapest_listings)) / count

def is_matching_listing(listing, sections, exact_sections):
    if exact_sections:
        return listing["section"] in sections
    else:
        return any(section in listing["section"] for section in sections)

def main():
    rows = get_sheet_rows()
    avg_price_values = list(map(get_avg_price, rows))

    print(avg_price_values)

    # update_sheet(avg_price_values)


main()








