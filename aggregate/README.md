# Aggregate Query Module

RESTful API-based aggregate queries for Visier Platform (no SDK dependencies).

## Quick Start

```bash
# Run query with default example
python aggregate/scripts/run_query.py

# Run with custom payload
python aggregate/scripts/run_query.py --file aggregate/examples/query_payload_examples.json
```

## Structure

```
aggregate/
├── aggregate_query_vanilla.py    # Core query functions
├── scripts/                       # CLI tools
│   ├── run_query.py               # Main query runner
│   └── discover_dimension_levels.py  # Dimension level discovery
├── examples/                      # Example payloads
│   ├── query_payload_examples.json
│   └── query_payload_examples_org_hierarchy.json
├── docs/                          # Documentation
│   ├── README.md                  # Detailed usage guide
│   └── LEARNINGS.md               # Query patterns and best practices
├── tests/                         # Test scripts
└── output/                         # Query results (CSV files)
```

## Documentation

- **[Usage Guide](docs/README.md)** - Complete guide with examples
- **[Learnings](docs/LEARNINGS.md)** - Query patterns, time intervals, and best practices
- **[Examples](examples/README.md)** - Example payload files

## Features

- ✅ RESTful API queries (no SDK dependencies)
- ✅ Helper functions for building queries
- ✅ Dimension member filtering
- ✅ Time interval support
- ✅ Direct CSV export via CLI tool
- ✅ JSON payload-based queries

## Usage in Python

```python
from aggregate.aggregate_query_vanilla import (
    execute_vanilla_aggregate_query,
    convert_vanilla_response_to_dataframe,
    create_dimension_axis
)

# Build and execute query
axes = [create_dimension_axis("Function")]
response = execute_vanilla_aggregate_query(metric_id="employeeCount", axes=axes)
df = convert_vanilla_response_to_dataframe(response, metric_id="employeeCount")
```

See [docs/README.md](docs/README.md) for complete documentation.
