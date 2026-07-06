# API Shadow Compare

Compare old and new API response captures and list the behavioral drift.

![API Shadow Compare cover](assets/readme-cover.svg)

## What counts as drift

- missing or extra response IDs
- status code changes
- fields added or removed from nested response bodies
- value changes on matching fields
- latency regressions beyond the configured ratio

## Run the example pair

```bash
git clone https://github.com/mertefekurt/api-shadow-compare.git
cd api-shadow-compare
python -m pip install -e ".[dev]"
api-shadow-compare examples/old.jsonl examples/new.jsonl
api-shadow-compare examples/old.jsonl examples/new.jsonl --json
```

The plain output is easy to read in a terminal; JSON is there when the comparison needs to feed another tool.
