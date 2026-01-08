# Archive

This directory contains deprecated or unused implementations.

## Files

- **`aggregate_query.py`** - SDK-based aggregate query implementation (deprecated)
  - Replaced by `aggregate/aggregate_query_vanilla.py` (RESTful API implementation)
  - Kept for reference only

- **`metric_discovery.py`** - Metric discovery utility (not currently needed)
  - Can be restored if metric discovery is needed in the future

- **`METRIC_ID_EXAMPLES.md`** - Metric ID examples (deprecated)
  - Information moved to aggregate query documentation

## Why Archived?

The RESTful API implementation (`aggregate/aggregate_query_vanilla.py`) is:
- Simpler to use
- More reliable (no SDK model mismatches)
- Easier to maintain
- Better documented

The SDK-based aggregate query had workarounds for SDK limitations and is no longer needed.
