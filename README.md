# nextendo-population

A GitHub Actions cron job that polls Nextendo's public `/api/online-counts`
endpoint every 15 minutes and maintains a rolling, per-title, per-hour-of-day
average player count in `data/population.json`. No auth, no server-side
changes to Nextendo itself -- this just samples the same public endpoint the
citron client already calls.

## Data format

```json
{
  "updated_utc": "2026-08-09T02:15:00Z",
  "games": {
    "<title_id, lowercase hex>": {
      "hours": [
        {"avg": 12.4, "samples": 340},
        ...
      ]
    }
  }
}
```

`hours` has 24 entries, index 0 = midnight UTC through index 23 = 23:00 UTC.
`avg` is a running mean of every sample taken in that UTC hour since the
repo started scraping; `samples` is how many polls have landed in that
bucket. The file stays a fixed size forever -- new samples update the
running average in place, they don't append to a growing log.

Consumers should rotate the 24-entry array to the viewer's own UTC offset
before rendering, so the bars line up with local time of day.

## Consuming it

```
https://raw.githubusercontent.com/<owner>/nextendo-population/main/data/population.json
```

## Local testing

```
python3 scripts/scrape.py
```
