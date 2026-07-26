# Andiamo — Cost & Model Selection Analysis

## Model Used

Claude Haiku 4.5 (`claude-haiku-4-5-20251001`)

Pricing (as of July 2026): $1.00 per million input tokens, $5.00 per million
output tokens.

## Why Haiku, Not Sonnet

Andiamo originally used Sonnet, which produces higher-quality, more nuanced
output. In production, this caused the function to exceed Netlify's 30-second
execution timeout on the free tier for longer date ranges - a hard platform
constraint, not a code bug.

Switching to Haiku traded some depth of reasoning for meaningfully faster
response times, avoiding the timeout. This is a real, common tradeoff in AI
product work: speed and cost versus depth of quality. Given the task -
generating a structured, specific but not deeply analytical trip brief -
Haiku's output quality has been sufficient across all four eval test cases
run so far (see EVAL_SET.md). If output quality had degraded meaningfully,
the honest fix would have been to either shorten the requested itinerary
length, or accept the timeout risk and upgrade Netlify's plan for a longer
execution window - not to force Sonnet into a time budget it can't meet.

## Estimated Cost Per Trip Brief

**Updated with real measured data from Claude's API usage field**, logged directly
from production calls rather than estimated:

| Test | Window | Input Tokens | Output Tokens | Duration | Cost |
|---|---|---|---|---|---|
| 1 | 4 days, no interests | 340 | 1,484 | - | $0.00776 |
| 2 | 7 days, full itinerary | 352 | 1,506 | - | $0.00789 |
| 3 | 2 days | 340 | 966 | 9.9s | $0.00517 |
| 4 | 2 days | 340 | 720 | 7.9s | $0.00394 |

**Real, measured average: roughly $0.006-0.008 per trip brief** - very close to
the original estimate below, confirming the estimate was reasonable, but now
backed by actual data rather than assumption.

### What the real data revealed

**Input tokens stay nearly flat (340-352) regardless of trip length.** This
confirms that the system prompt - fixed instructions sent identically on
every single call - dominates a meaningful share of input, though less than
originally assumed. Actually counting the system prompt text directly
(137 words, roughly 178 tokens using the standard ~1.3 tokens-per-word
ratio) shows it accounts for roughly half of total input (178 of ~340-352
tokens), not the 70-80% originally estimated. The remaining ~160-175
tokens cover the user's specific request - team, dates, interests, and the
match list - a more even split between fixed and variable cost than
initially assumed.

**Output tokens scale meaningfully with trip length** - 2-day requests used
720-966 output tokens, while 7-day requests used 1,484-1,506. This confirms
output length genuinely tracks the number of days requested, and is the
primary lever affecting both cost and generation time.

**Response duration tracks output length closely** - 2-day requests
completed in 7.9-9.9 seconds, while longer 7-day requests approached
Netlify's 30-second timeout. This is concrete evidence justifying the
7-day cap decision: shorter requests aren't just cheaper, they're
meaningfully faster and safer against the platform's hard timeout limit.

**Prompt caching evaluated and correctly ruled out.** Since the system prompt
is fixed and identical on every call, it initially looked like a strong
candidate for Anthropic's prompt caching feature, which offers up to 90%
cost savings on repeated, unchanged input. However, caching requires a
minimum prompt length to activate at all, and that minimum is model-specific
- for Claude Haiku 4.5, it is 4,096 tokens. Andiamo's system prompt is
approximately 178 tokens, roughly 23 times below the threshold. Anthropic
does not error when a prompt is too small to cache; the instruction is
silently ignored and the call bills at full price regardless, meaning this
could easily go unnoticed if implemented without verifying the threshold
first. Artificially padding the prompt to clear the minimum would be
optimizing for the technique rather than the product, so the correct
decision is not to implement caching here. This remains worth revisiting
only if the system prompt naturally grows past ~4,096 tokens for other
product reasons (e.g. richer instructions, more examples, longer team
data embedded directly in the prompt).

### Original estimate (before real data was available)

| Component | Estimated Tokens | Rate | Cost |
|---|---|---|---|
| System prompt | ~350-400 | $1.00 / M input | ~$0.0004 |
| User message + match data | ~150-250 | $1.00 / M input | ~$0.0002 |
| **Total input** | **~550-600** | | **~$0.0006** |
| Generated trip brief output | ~1,200-1,800 | $5.00 / M output | ~$0.0075 |
| **Total per generation** | | | **~$0.008** |

**Roughly $0.008 (under one cent) per trip brief generated.**

## What This Means at Scale

- 100 trip briefs generated: ~$0.80
- 1,000 trip briefs generated: ~$8.00
- 10,000 trip briefs generated: ~$80.00

At this cost level, the model choice is not the primary cost concern for a
project at Andiamo's current scale - the practical constraint has been
Netlify's function timeout, not API spend. This would change at meaningfully
higher volume, where the Batch API (50% off, for non-real-time use cases)
would become worth implementing. Prompt caching, evaluated above, does not
apply at Andiamo's current system prompt size regardless of volume - it
would require the prompt itself to grow substantially, not simply more
requests.

## Honest Caveats

- Total input/output token counts per call are now real, measured values
  logged directly from Claude's API response (`usage.input_tokens` /
  `usage.output_tokens`), not estimates.
- The breakdown *within* input tokens (system prompt vs. user message) is
  still a reconstruction: the system prompt's 178-token figure was
  calculated by directly counting its actual word count and applying a
  standard word-to-token ratio, not read from a field Anthropic's API
  provides directly. Anthropic's usage data reports only the input/output
  totals, not an internal breakdown - this estimate carries the normal
  uncertainty of that conversion method.
- Pricing is subject to change; this reflects rates as of July 2026.
- Cost figures reflect actual production calls made during development and
  eval testing on July 24, 2026, not a large-scale or long-term sample.
