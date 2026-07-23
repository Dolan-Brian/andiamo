import requests
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from anthropic import Anthropic
from serie_a_teams import get_team_info

load_dotenv()

FOOTBALL_API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")
FOOTBALL_BASE_URL = "https://api.football-data.org/v4"

client = Anthropic()


def get_fixtures_for_team(team_name, date_from, date_to):
    """
    Fetches Serie A fixtures for a specific team within a date range.
    Returns a list of matches enriched with city/stadium info.
    """
    headers = {"X-Auth-Token": FOOTBALL_API_KEY}

    params = {
        "dateFrom": date_from,
        "dateTo": date_to,
    }

    response = requests.get(
        f"{FOOTBALL_BASE_URL}/competitions/SA/matches",
        headers=headers,
        params=params,
    )

    if response.status_code != 200:
        print(f"Error fetching fixtures: {response.status_code} - {response.text}")
        return []

    data = response.json()
    all_matches = data.get("matches", [])

    # Filter to matches involving our target team
    team_matches = []
    for match in all_matches:
        home = match["homeTeam"]["name"]
        away = match["awayTeam"]["name"]

        if team_name in (home, away):
            # The match is at the home team's stadium
            venue_team = home
            venue_info = get_team_info(venue_team)

            team_matches.append({
                "date": match["utcDate"],
                "home_team": home,
                "away_team": away,
                "city": venue_info["city"],
                "stadium": venue_info["stadium"],
                "status": match["status"],
            })

    return team_matches


def generate_trip_brief(team_name, matches, travel_window, interests):
    """
    Sends match data and preferences to Claude to generate a structured trip brief.
    """
    matches_text = "\n".join([
        f"- {m['date']}: {m['home_team']} vs {m['away_team']} at {m['stadium']}, {m['city']}"
        for m in matches
    ])

    system_prompt = """You are a knowledgeable Italy travel planner who specializes in
combining football (calcio) attendance with authentic Italian travel experiences.

You write trip briefs that are specific and practical, never generic travel-blog fluff.
You understand Italian football culture, regional food specialties, and how to sequence
a trip efficiently between cities.

Structure every trip brief with these sections:
1. TRIP OVERVIEW - a 2-3 sentence summary of the trip concept
2. MATCH SCHEDULE - the games to attend, in chronological order
3. SUGGESTED ITINERARY - a day-by-day rough structure connecting the matches with travel and activities
4. PRACTICAL NOTES - tickets, transport between cities, anything the traveler should know

Be specific. Reference actual neighborhoods, real regional dishes, and realistic travel times
between Italian cities. Do not pad with generic travel advice."""

    user_message = f"""Create a trip brief for a football fan planning to attend matches
featuring {team_name} during {travel_window}.

Interests: {interests}

Available matches during this window:
{matches_text}

Build a trip brief around attending these matches."""

    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1500,
        system=system_prompt,
        messages=[
            {"role": "user", "content": user_message}
        ]
    )

    return message.content[0].text


if __name__ == "__main__":
    # Hardcoded test case
    TEAM = "Como 1907"
    DATE_FROM = "2026-09-01"
    DATE_TO = "2026-09-14"
    INTERESTS = "food, architecture, lake views, relaxed pace"

    print(f"Fetching {TEAM} fixtures between {DATE_FROM} and {DATE_TO}...\n")

    matches = get_fixtures_for_team(TEAM, DATE_FROM, DATE_TO)

    if not matches:
        print("No matches found for this team in this date range.")
    else:
        print(f"Found {len(matches)} match(es):")
        for m in matches:
            print(f"  {m['date']} - {m['home_team']} vs {m['away_team']} at {m['stadium']}, {m['city']}")

        print("\nGenerating trip brief with Claude...\n")
        brief = generate_trip_brief(TEAM, matches, f"{DATE_FROM} to {DATE_TO}", INTERESTS)

        print("=" * 60)
        print(brief)
        print("=" * 60)
