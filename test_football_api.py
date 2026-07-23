import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")
BASE_URL = "https://api.football-data.org/v4"

headers = {
    "X-Auth-Token": API_KEY
}

# Serie A competition code is "SA"
response = requests.get(f"{BASE_URL}/competitions/SA/matches", headers=headers)

print(f"Status code: {response.status_code}")

# Check rate limit headers - important per football-data.org's guidance
print(f"\nRate limit info from headers:")
for key in response.headers:
    if "x-request" in key.lower() or "x-ratelimit" in key.lower():
        print(f"  {key}: {response.headers[key]}")

if response.status_code == 200:
    data = response.json()
    matches = data.get("matches", [])
    print(f"\nTotal matches found: {len(matches)}")

    # Show the first 5 upcoming matches
    print("\nFirst 5 matches:")
    for match in matches[:5]:
        home = match["homeTeam"]["name"]
        away = match["awayTeam"]["name"]
        date = match["utcDate"]
        status = match["status"]
        venue = match.get("venue", "Venue not listed")
        print(f"  {date} - {home} vs {away} ({status}) at {venue}")
else:
    print(f"\nError response: {response.text}")
