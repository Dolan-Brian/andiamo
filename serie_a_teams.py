"""
Serie A 2026-27 team to city/stadium mapping.

This is static reference data - team home cities and stadiums rarely change,
so it's maintained as a hardcoded dictionary rather than fetched from an API.
The football-data.org fixtures endpoint returns team names but not venue
details, so this fills that gap.

Source: compiled from public football reference sites, current for the
2026-27 Serie A season (20 teams).
"""

SERIE_A_TEAMS = {
    "FC Internazionale Milano": {"city": "Milan", "stadium": "San Siro"},
    "AC Milan": {"city": "Milan", "stadium": "San Siro"},
    "SSC Napoli": {"city": "Naples", "stadium": "Stadio Diego Armando Maradona"},
    "AS Roma": {"city": "Rome", "stadium": "Stadio Olimpico"},
    "SS Lazio": {"city": "Rome", "stadium": "Stadio Olimpico"},
    "Juventus FC": {"city": "Turin", "stadium": "Allianz Stadium"},
    "Torino FC": {"city": "Turin", "stadium": "Stadio Olimpico Grande Torino"},
    "Como 1907": {"city": "Como", "stadium": "Stadio Giuseppe Sinigaglia"},
    "Atalanta BC": {"city": "Bergamo", "stadium": "Gewiss Stadium"},
    "Bologna FC 1909": {"city": "Bologna", "stadium": "Stadio Renato Dall'Ara"},
    "Udinese Calcio": {"city": "Udine", "stadium": "Bluenergy Stadium"},
    "Genoa CFC": {"city": "Genoa", "stadium": "Stadio Luigi Ferraris"},
    "ACF Fiorentina": {"city": "Florence", "stadium": "Stadio Artemio Franchi"},
    "US Sassuolo Calcio": {"city": "Sassuolo", "stadium": "Mapei Stadium"},
    "Cagliari Calcio": {"city": "Cagliari", "stadium": "Unipol Domus"},
    "Parma Calcio 1913": {"city": "Parma", "stadium": "Stadio Ennio Tardini"},
    "US Lecce": {"city": "Lecce", "stadium": "Stadio Via del Mare"},
    "AC Monza": {"city": "Monza", "stadium": "Stadio Brianteo"},
    "Frosinone Calcio": {"city": "Frosinone", "stadium": "Stadio Benito Stirpe"},
    "Venezia FC": {"city": "Venice", "stadium": "Stadio Pierluigi Penzo"},
}


def get_team_info(team_name):
    """
    Look up city and stadium for a Serie A team.
    Returns a dict with 'city' and 'stadium', or a fallback if not found.
    """
    return SERIE_A_TEAMS.get(
        team_name,
        {"city": "Unknown", "stadium": "Unknown - team not in current mapping"}
    )


if __name__ == "__main__":
    # Quick test
    for team, info in SERIE_A_TEAMS.items():
        print(f"{team}: {info['city']} ({info['stadium']})")
