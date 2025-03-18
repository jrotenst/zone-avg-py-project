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

    # Get date from specified sheet ID and range
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="Zones!A2:F14"
    ).execute()

    return result.get("values", [])

def update_sheet(values):
    print("\nUpdating sheet...")

    # Format list of values for Sheets API
    data = {"values": [[value] for value in values]}

    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range="Zones!H2:H14",
        valueInputOption="RAW",
        body=data
    ).execute()

    print("Sheet updated successfully!")

def get_avg_price(row):
    print("\nGetting avg price for row...")

    name = row[0]
    sections = row[1].split(",")
    exact_sections = row[2] == "Y"
    count = int(row[5])

    print(f"Name: {name}, Sections: {sections}, Exact Sections: {exact_sections}, Count: {count}")

    print("Finding matching listings for row...")

    # Find matching listings for row (zone)
    matching_listings = list(filter(lambda listing: is_matching_listing(listing, sections, exact_sections), LISTINGS))

    # Sort listings by price (low-to-high) and slice by count
    matching_listings.sort(key=lambda listing: listing["price"])
    cheapest_listings = matching_listings[:count]

    listing_sections = ", ".join([listing["section"] for listing in cheapest_listings])
    print(f"Matching listings for row {name}: \n{listing_sections}")

    price_strings = ", ".join([str(listing["price"]) for listing in cheapest_listings])
    print(f"Cheapest listings for row {name}: \n{price_strings}")

    # Return sum of all prices divided by count, rounded down to 2 decimals
    avg = round(sum(map(lambda listing: listing["price"], cheapest_listings)) / count, 2)
    print(f"Average: {avg}")

    return avg

def is_matching_listing(listing, sections, exact_sections):
    if exact_sections:
        return listing["section"] in sections
    else:
        return any(section in listing["section"] for section in sections)

def main():
    print("Starting main...")
    rows = get_sheet_rows()
    avg_price_values = list(map(get_avg_price, rows))

    # Write the averages generated for each into the H column
    update_sheet(avg_price_values)

    print(f"\nAverage Prices: \n{avg_price_values}")

main()








