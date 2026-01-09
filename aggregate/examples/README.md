# Query Payload Examples

This directory contains example JSON payloads for Visier aggregate queries.

## Files

- **query_payload_examples.json** - Basic example with Country_Cost dimension
- **query_payload_examples_org_hierarchy.json** - Example with Organization_Hierarchy, Location, and Country_Cost dimensions

## Usage

Use these examples with the `run_query.py` script:

```bash
# Run with basic example
python aggregate/scripts/run_query.py --file aggregate/examples/query_payload_examples.json

# Run with organization hierarchy example
python aggregate/scripts/run_query.py --file aggregate/examples/query_payload_examples_org_hierarchy.json
```

## Customizing

Edit the JSON files to customize:
- Metrics (`query.source.metric`)
- Dimensions/axes (`query.axes`)
- Filters (`query.filters`)
- Time intervals (`query.timeIntervals`)
- Options (`options`)

See `aggregate/docs/LEARNINGS.md` for detailed patterns and examples.
