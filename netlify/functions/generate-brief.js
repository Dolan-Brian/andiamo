// netlify/functions/generate-brief.js
//
// This function runs on Netlify's servers, not in the user's browser.
// That's what keeps FOOTBALL_DATA_API_KEY and ANTHROPIC_API_KEY secret -
// they're set as environment variables in the Netlify dashboard and are
// never exposed to anyone visiting the site.

const SERIE_A_TEAMS = {
  "FC Internazionale Milano": { city: "Milan", stadium: "San Siro" },
  "AC Milan": { city: "Milan", stadium: "San Siro" },
  "SSC Napoli": { city: "Naples", stadium: "Stadio Diego Armando Maradona" },
  "AS Roma": { city: "Rome", stadium: "Stadio Olimpico" },
  "SS Lazio": { city: "Rome", stadium: "Stadio Olimpico" },
  "Juventus FC": { city: "Turin", stadium: "Allianz Stadium" },
  "Torino FC": { city: "Turin", stadium: "Stadio Olimpico Grande Torino" },
  "Como 1907": { city: "Como", stadium: "Stadio Giuseppe Sinigaglia" },
  "Atalanta BC": { city: "Bergamo", stadium: "Gewiss Stadium" },
  "Bologna FC 1909": { city: "Bologna", stadium: "Stadio Renato Dall'Ara" },
  "Udinese Calcio": { city: "Udine", stadium: "Bluenergy Stadium" },
  "Genoa CFC": { city: "Genoa", stadium: "Stadio Luigi Ferraris" },
  "ACF Fiorentina": { city: "Florence", stadium: "Stadio Artemio Franchi" },
  "US Sassuolo Calcio": { city: "Sassuolo", stadium: "Mapei Stadium" },
  "Cagliari Calcio": { city: "Cagliari", stadium: "Unipol Domus" },
  "Parma Calcio 1913": { city: "Parma", stadium: "Stadio Ennio Tardini" },
  "US Lecce": { city: "Lecce", stadium: "Stadio Via del Mare" },
  "AC Monza": { city: "Monza", stadium: "Stadio Brianteo" },
  "Frosinone Calcio": { city: "Frosinone", stadium: "Stadio Benito Stirpe" },
  "Venezia FC": { city: "Venice", stadium: "Stadio Pierluigi Penzo" },
};

function getTeamInfo(name) {
  return SERIE_A_TEAMS[name] || { city: "Unknown", stadium: "Unknown" };
}

exports.handler = async function (event) {
  if (event.httpMethod !== "POST") {
    return { statusCode: 405, body: "Method not allowed" };
  }

  try {
    const { team, dateFrom, dateTo, interests } = JSON.parse(event.body);

    if (!team || !dateFrom || !dateTo) {
      return { statusCode: 400, body: "Missing team, dateFrom, or dateTo" };
    }

    // --- Step 1: fetch Serie A fixtures from football-data.org ---
    const fixturesRes = await fetch(
      `https://api.football-data.org/v4/competitions/SA/matches?dateFrom=${dateFrom}&dateTo=${dateTo}`,
      { headers: { "X-Auth-Token": process.env.FOOTBALL_DATA_API_KEY } }
    );

    if (!fixturesRes.ok) {
      const errText = await fixturesRes.text();
      return { statusCode: 502, body: `Football data error: ${errText}` };
    }

    const fixturesData = await fixturesRes.json();
    const allMatches = fixturesData.matches || [];

    // --- Step 2: filter to the selected team, enrich with city/stadium ---
    const teamMatches = allMatches
      .filter((m) => m.homeTeam.name === team || m.awayTeam.name === team)
      .map((m) => {
        const venueInfo = getTeamInfo(m.homeTeam.name);
        return {
          date: m.utcDate.split("T")[0],
          home_team: m.homeTeam.name,
          away_team: m.awayTeam.name,
          city: venueInfo.city,
          stadium: venueInfo.stadium,
        };
      });

    if (teamMatches.length === 0) {
      return {
        statusCode: 200,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ trip_overview: "", days: [], practical_notes: [] }),
      };
    }

    // --- Step 3: ask Claude to build a structured trip brief ---
    const matchesText = teamMatches
      .map((m) => `- ${m.date}: ${m.home_team} vs ${m.away_team} at ${m.stadium}, ${m.city}`)
      .join("\n");

    const systemPrompt = `You are a knowledgeable Italy travel planner who specializes in combining football (calcio) attendance with authentic Italian travel experiences.

You write trip briefs that are specific and practical, never generic travel-blog fluff. Reference real neighborhoods, real regional dishes, and realistic travel times between Italian cities.

Respond with ONLY valid JSON, no markdown fences, no commentary, matching exactly this shape:

{
  "trip_overview": "2-3 sentence summary of the trip concept",
  "days": [
    {
      "date": "YYYY-MM-DD",
      "title": "short descriptive title for this day",
      "is_match_day": true or false,
      "match": {"home": "...", "away": "...", "stadium": "...", "city": "..."} or null if not a match day,
      "activities": ["specific activity 1", "specific activity 2", "specific activity 3"]
    }
  ],
  "practical_notes": ["note 1", "note 2", "note 3"]
}

Cover every day in the requested travel window, not just match days. Sequence travel between cities realistically.`;

    const userMessage = `Create a trip brief for a football fan following ${team} between ${dateFrom} and ${dateTo}.

Interests: ${interests}

Available matches:
${matchesText}`;

    const claudeRes = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": process.env.ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
      },
      body: JSON.stringify({
        model: "claude-haiku-4-5-20251001",
        max_tokens: 2000,
        system: systemPrompt,
        messages: [{ role: "user", content: userMessage }],
      }),
    });

    if (!claudeRes.ok) {
      const errText = await claudeRes.text();
      return { statusCode: 502, body: `Claude API error: ${errText}` };
    }

    const claudeData = await claudeRes.json();
    let rawText = claudeData.content[0].text.trim();

    // Strip markdown fences if Claude includes them despite instructions
    rawText = rawText.replace(/^```json\s*/i, "").replace(/```$/, "").trim();

    const tripBrief = JSON.parse(rawText);

    return {
      statusCode: 200,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(tripBrief),
    };
  } catch (err) {
    return { statusCode: 500, body: `Server error: ${err.message}` };
  }
};
