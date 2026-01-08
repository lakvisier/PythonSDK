# Vanilla Aggregate Query - Simple Usage Guide

The `aggregate_query_vanilla.py` module provides a simple, easy-to-use interface for querying Visier metrics without the SDK.

## Quick Start

### Basic Usage

```python
from aggregate_query_vanilla import query_metric

# Query a metric by dimension(s) - last 6 months
df = query_metric("employeeCount", dimensions=["Function"])

# Multiple dimensions
df = query_metric("employeeCount", dimensions=["Function", "Gender"])

# Save directly to CSV
df = query_metric("employeeCount", dimensions=["Function"], save_csv="results.csv")
```

### Time Periods

```python
# Last 12 months
df = query_metric("employeeCount", dimensions=["Function"], months=12)

# Next 3 months (forward)
df = query_metric("employeeCount", dimensions=["Function"], months=3, direction="FORWARD")
```

### Different Analytic Objects

```python
# For Applicant data
df = query_metric("applicantCount", dimensions=["Application_Source"], qualifying_path="Applicant")
```

## Function Reference

### `query_metric()` - Simple Query Function

The easiest way to query metrics.

**Parameters:**
- `metric_id` (str, required): Metric to query (e.g., "employeeCount")
- `dimensions` (list, required): List of dimension names (e.g., ["Function", "Gender"])
- `qualifying_path` (str, optional): Qualifying path (default: "Employee")
- `months` (int, optional): Number of months (default: 6)
- `direction` (str, optional): "BACKWARD" (last N months) or "FORWARD" (next N months)
- `save_csv` (str, optional): Filename to save results as CSV
- `filters` (list, optional): Advanced filter definitions
- `options` (dict, optional): Query options

**Returns:** pandas DataFrame

**Example:**
```python
df = query_metric(
    metric_id="employeeCount",
    dimensions=["Function", "Pay_Level"],
    months=6,
    save_csv="employee_counts.csv"
)
```

### `create_dimension_axis()` - Helper for Custom Queries

Create a dimension axis for use in advanced queries.

**Example:**
```python
from aggregate_query_vanilla import create_dimension_axis, execute_vanilla_aggregate_query

axis = create_dimension_axis("Function", qualifying_path="Employee")
response = execute_vanilla_aggregate_query(
    metric_id="employeeCount",
    axes=[axis]
)
```

### `execute_vanilla_aggregate_query()` - Advanced Usage

Full control over query structure.

**Example:**
```python
from aggregate_query_vanilla import execute_vanilla_aggregate_query

response = execute_vanilla_aggregate_query(
    metric_id="employeeCount",
    axes=[{
        "dimensionLevelSelection": {
            "dimension": {"name": "Function", "qualifyingPath": "Employee"},
            "levelIds": ["Function"]
        }
    }],
    time_intervals={
        "dynamicDateFrom": "SOURCE",
        "intervalPeriodType": "MONTH",
        "intervalCount": 6,
        "direction": "BACKWARD"
    }
)
```

## Common Use Cases

### 1. Employee Count by Department

```python
df = query_metric("employeeCount", dimensions=["Function"])
```

### 2. Employee Count by Gender and Department

```python
df = query_metric("employeeCount", dimensions=["Function", "Gender"])
```

### 3. Last 12 Months of Data

```python
df = query_metric("employeeCount", dimensions=["Function"], months=12)
```

### 4. Export to CSV

```python
df = query_metric("employeeCount", dimensions=["Function"], save_csv="results.csv")
```

### 5. Filter Results in Python

```python
df = query_metric("employeeCount", dimensions=["Function"])
# Filter to specific function
customer_support = df[df["Function"] == "Customer Support"]
```

## Finding Available Metrics

Use the metric discovery utility:

```bash
python metric_discovery.py
```

Or search for specific metrics:

```python
from metric_discovery import search_metrics, get_sdk_config
from visier_platform_sdk import ApiClient, Configuration

config = get_sdk_config()
api_client = ApiClient(config)

# Search for metrics
df = search_metrics(api_client, search_term="employee")
print(df)
```

## Environment Setup

Create a `.env` file with your credentials:

```bash
VISIER_HOST=https://your-tenant.api.visier.io
VISIER_APIKEY=your-api-key
VISIER_VANITY=your-vanity
VISIER_USERNAME=your-username
VISIER_PASSWORD=your-password
```

## Command Line Usage

Run the demo:

```bash
python aggregate_query_vanilla.py
```

This will:
1. Query `employeeCount` by `Function` and `Pay_Level`
2. Get last 6 months of data
3. Save results to `aggregate_query_results.csv`

## Troubleshooting

### "At least one dimension is required"

Make sure you provide at least one dimension:

```python
df = query_metric("employeeCount", dimensions=["Function"])  # ✓ Correct
df = query_metric("employeeCount")  # ✗ Missing dimensions
```

### "No data returned"

- Try a different time period
- Check if the metric exists in your tenant
- Verify you have permissions for the data

### Authentication Errors

- Verify your `.env` file has all required variables
- Check that credentials are correct
- Ensure your API key is valid

## Advanced: Custom Time Intervals

For more control over time periods:

```python
from aggregate_query_vanilla import execute_vanilla_aggregate_query, create_dimension_axis

response = execute_vanilla_aggregate_query(
    metric_id="employeeCount",
    axes=[create_dimension_axis("Function")],
    time_intervals={
        "fromDateTime": "2024-01-01",
        "intervalPeriodType": "MONTH",
        "intervalCount": 12
    }
)
```

## See Also

- `AGGREGATE_QUERY_API_REFERENCE.md` - Full API schema reference
- `aggregate_query.py` - SDK-based implementation (with workaround)
- Postman Collection: https://www.postman.com/visier-alpine/visier-alpine-platform/overview
