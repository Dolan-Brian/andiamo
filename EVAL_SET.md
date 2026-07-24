# Andiamo — Eval Set

An eval set defines what "good enough to ship" means for a feature that
produces a different, non-deterministic response every time it runs. Rather
than asserting one exact expected output, each test case below defines the
qualities a good response must have, and the known failure modes to check
for. This is the AI-native equivalent of acceptance criteria.

---

## Test Case 1 — Happy Path (Baseline)

**Input:** Team: Como 1907 · Window: Sept 1-7 · Interests: food, lake views

**What "good" looks like:**
- Correctly identifies real Como fixtures within the window
- Itinerary content is specific — real neighborhoods, real restaurants or
  dish names, not generic travel-blog language
- Reflects Como/Lake Como geography accurately (lake activities, ferry
  travel between towns, correct town names)
- Match day sequencing is logistically sensible

**Known failure modes to check for:**
- Generic filler content instead of specifics
- Truncated JSON response if the window is too long relative to token limit
- Function timeout if response generation takes too long

---

## Test Case 2 — Interest Fidelity Check

**Input:** Team: Juventus FC · Window: Sept 1-7 · Interests: architecture,
history

**What "good" looks like:**
- Correctly identifies real Juventus fixtures within the window
- Content genuinely reflects architecture/history interests — specific real
  landmarks (e.g. Egyptian Museum, Palazzo Reale, the Duomo), not generic
  "explore the city" language
- Does NOT default to heavy food content just because that performed well
  in other tests — this checks whether stated interests actually shape the
  output, rather than being ignored
- Correctly reflects Turin specifically

**Known failure modes to check for:**
- Interests being ignored in favor of generic or food-heavy content
  regardless of what was requested
- City/team confusion

---

## Test Case 3 — No Matches for Chosen Team (Fallback Behavior)

**Input:** A team confirmed to have zero fixtures in a short test window ·
Interests: any

**What "good" looks like:**
- Does NOT show a plain error or dead end
- Clearly and honestly tells the user their chosen team isn't playing
  during this window
- Searches only within the originally requested date window (does not
  extend the search period)
- Identifies the Serie A fixture(s) happening within that window that are
  geographically closest to the originally chosen team's home city
  (using general knowledge of Italian geography, not precise distance data)
- Builds a full-quality trip brief around that alternate match - same
  standard as a normal request
- Clearly communicates that this is an alternate match, not the
  originally requested team
- If nothing is happening in Serie A at all within the window (e.g. true
  off-season), falls back to a simple, honest message rather than
  reaching further than two weeks out

**Known failure modes to check for:**
- Hallucinating a fixture that doesn't actually exist instead of correctly
  reporting none in range
- Incorrect or vague sense of Italian geography when judging "closest"
- Confusing or misleading framing that implies the original team is
  somehow involved

---

## Test Case 4 — Unique City Logistics + Pace Constraint

**Input:** Team: Venezia FC · Window: Oct 1-7 · Interests: relaxed pace

**What "good" looks like:**
- Correctly identifies real Venezia fixtures within the window
- Itinerary genuinely respects "relaxed pace" - noticeably less packed than
  a "packed schedule" request would be
- Correctly handles Venice's unique car-free geography - walking and
  vaporetto (water bus) references, not generic driving/train directions
- Correctly reflects that Venezia FC's stadium (Stadio Pierluigi Penzo) is
  on the Lido, a separate island from mainland Venice - not conflated with
  central Venice logistics

**Known failure modes to check for:**
- Generic Italian city advice that ignores Venice's unusual geography
- Getting the Lido/mainland stadium location wrong
- "Relaxed pace" being ignored in favor of a packed schedule

---

## How to Use This Eval Set

Run each test case through Andiamo. For each, score against the "what good
looks like" criteria (pass / partial / fail) and note whether any listed
failure mode actually occurred. Document real results below as they're run,
so this file becomes a living record of the feature's actual reliability
over time - not just its intended behavior.

## Results Log

| Test Case | Date Run | Result | Notes |
|---|---|---|---|
| 1 - Happy Path | Jul 24 | PASS | Tested with Como 1907, Sept 1-7, food/lake views. Correctly identified Genoa CFC vs Como 1907 (away match) on Sept 4. Content was genuinely specific throughout - real dish names (tinca ripiena, missoltini, pansotti, trofie al pesto), real neighborhoods (Caruggi, Porto Antico, Camerlata), correct ferry destinations (Bellagio, Varenna), realistic train times. Match day sequencing logical (travel day before, coastal day trip after). Product decision: for away matches, itinerary correctly weights time toward the match city (Genoa) over the followed team's home city (Como) - this is the intended design, since the goal is following the team and experiencing wherever they're actually playing, not staying anchored to their home city. Full pass. |
| 2 - Interest Fidelity | Jul 24 | PASS | Tested with Juventus FC, Sept 1-7, architecture/history interests. Correctly identified Juventus vs AC Milan at Allianz Stadium. Content genuinely reflected architecture/history throughout - specific real landmarks (Palazzo Madama, Egyptian Museum, Mole Antonelliana, Alessandria's Cittadella, Milan's Duomo and Sforza Castle) rather than generic filler. Food appeared only as texture (tajarin pasta, gianduja chocolate), not as the focus - confirms stated interests genuinely shape output rather than defaulting to food-heavy content seen in Test 1. Product decision: itinerary expanded beyond Turin into nearby Alessandria and Milan as day trips - judged as good travel-planning instinct rather than scope creep, since interests were broad (architecture/history generally) not city-specific. Full pass. |
| 3 - No Matches Fallback | Jul 24 | PASS | Tested with Como 1907, single-day window (Aug 23, 2026), no Como fixture that day. Correctly identified Atalanta BC vs US Sassuolo at Gewiss Stadium, Bergamo as the geographically closest available match (50km from Como). Clearly disclosed Como wasn't playing and explained why Bergamo was chosen. No hallucinated fixtures, no confusing framing. Full pass against all defined criteria. |
| 4 - Unique City Logistics | Jul 24 | PASS | Tested with Venezia FC, Oct 15-21 (first attempt at Oct 1-7 hit true off-season/international break with zero Serie A matches league-wide - correctly triggered honest off-season message, not a bug). Correctly identified Venezia FC vs SSC Napoli on Oct 18. "Relaxed pace" genuinely reflected in tone and structure ("unhurried," "without rushing," long unstructured afternoons) - visibly different density than the packed Turin itinerary in Test 2. Vaporetto (water bus) used correctly and consistently for all inter-island travel (Murano, Burano, Torcello) with no car/generic-transit confusion. Correctly identified that Stadio Pierluigi Penzo is on the island of Sant'Elena, distinct from central Venice, with accurate travel time (15 min vaporetto) - this was the specific known risk flagged in the eval criteria and it passed. Full pass. |
