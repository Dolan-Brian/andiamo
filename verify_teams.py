import requests
import os
from dotenv import load_dotenv
from serie_a_teams import SERIE_A_TEAMS

load_dotenv()

API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")
BASE_URL = "https://api.football-data.org/v4"

headers = {
    "X-Auth-Token": API_KEY
}

response = requests.get(f"{BASE_URL}/competitions/SA/teams", headers=headers)

print(f"Status code: {response.status_code}\n")

if response.status_code == 200:
    data = response.json()
    api_teams = [team["name"] for team in data.get("teams", [])]

    print(f"Total teams returned by API: {len(api_teams)}\n")

    print("=== Teams from API ===")
    for name in sorted(api_teams):
        print(f"  {name}")

    print(f"\n=== Checking against our mapping ===")
    our_teams = set(SERIE_A_TEAMS.keys())
    api_teams_set = set(api_teams)

    matched = our_teams & api_teams_set
    missing_from_ours = api_teams_set - our_teams
    extra_in_ours = our_teams - api_teams_set

    print(f"\nMatched exactly: {len(matched)} / {len(api_teams_set)}")

    if missing_from_ours:
        print(f"\nIn API but NOT in our mapping (need to add or rename):")
        for name in sorted(missing_from_ours):
            print(f"  {name}")

    if extra_in_ours:
        print(f"\nIn our mapping but NOT in API (may be misnamed or wrong team):")
        for name in sorted(extra_in_ours):
            print(f"  {name}")

else:
    print(f"Error response: {response.text}")
