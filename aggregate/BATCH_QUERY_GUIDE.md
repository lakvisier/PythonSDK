# Batch Query Guide: Querying 50+ Metrics Efficiently

This guide shows you how to query 50+ metrics efficiently with shared dimensions, dimension member filtering, and global filters.

## Overview

The `query_multiple_metrics()` function is designed for scenarios where you need to:
- Query many metrics (50+) at once
- Use the same dimensions for all metrics (2-3 dimensions)
- Focus on specific dimension members (e.g., only certain Functions)
- Apply global filters that work across all metrics

## Quick Example

```python
from aggregate_query_vanilla import (
    query_multiple_metrics,
    create_selection_concept_filter,
    create_member_set_filter
)

# Your list of 50 metrics
metric_ids = [
    "employeeCount",
    "turnoverRate",
    "headcount",
    "newHires",
    "terminations",
    # ... 45 more metrics
]

# Query all 50 metrics with:
# - Dimensions: Function and Gender
# - Dimension filter: Only Engineering and Sales functions
# - Global filter: Active employees only
df = query_multiple_metrics(
    metric_ids=metric_ids,
    dimensions=["Function", "Gender"],
    months=6,
    dimension_member_filters={
        "Function": ["Engineering", "Sales"]  # Only these functions
    },
    global_filters=[
        create_selection_concept_filter("isActive")  # Active employees only
    ],
    save_csv="all_50_metrics.csv"
)
```

## Function Parameters

### Required Parameters

- **`metric_ids`** (List[str]): List of metric IDs to query
  ```python
  metric_ids = ["employeeCount", "turnoverRate", "headcount"]
  ```

- **`dimensions`** (List[str]): List of dimension names for grouping
  ```python
  dimensions = ["Function", "Gender"]  # 2-3 dimensions work well
  ```

### Optional Parameters

- **`qualifying_path`** (str): Qualifying path for dimensions (default: "Employee")
  ```python
  qualifying_path = "Employee"  # or "Applicant" for applicant metrics
  ```

- **`months`** (int): Number of months to query (default: 6)
  ```python
  months = 12  # Last 12 months
  ```

- **`direction`** (str): "BACKWARD" (last N months) or "FORWARD" (next N months)
  ```python
  direction = "BACKWARD"  # or "FORWARD"
  ```

- **`dimension_member_filters`** (Dict[str, List[str]]): Filter to specific dimension members
  ```python
  dimension_member_filters = {
      "Function": ["Engineering", "Sales"],  # Only these functions
      "Gender": ["Male"]  # Only male employees
  }
  ```

- **`global_filters`** (List[Dict]): Filters that apply to all metrics
  ```python
  global_filters = [
      create_selection_concept_filter("isActive"),  # Active employees
      create_selection_concept_filter("isManager")  # Managers only
  ]
  ```

- **`options`** (Dict): Query options
  ```python
  options = {
      "zeroVisibility": "ELIMINATE",  # Hide zero values
      "nullVisibility": "ELIMINATE"   # Hide null values
  }
  ```

- **`save_csv`** (str): Filename to save results
  ```python
  save_csv = "all_metrics.csv"
  ```

- **`progress`** (bool): Show progress (default: True)
  ```python
  progress = True  # Show "Querying metric (1/50)..." messages
  ```

## Filter Types

### 1. Dimension Member Filters

Filter to specific members of a dimension:

```python
from aggregate_query_vanilla import create_member_set_filter

# Only include Engineering and Sales functions
filter = create_member_set_filter(
    dimension_name="Function",
    included_members=["Engineering", "Sales"]
)

# Or exclude specific members
filter = create_member_set_filter(
    dimension_name="Function",
    excluded_members=["HR", "Finance"]
)
```

### 2. Selection Concept Filters (Global)

Filter by selection concepts (e.g., isManager, isActive):

```python
from aggregate_query_vanilla import create_selection_concept_filter

# Only active employees
filter = create_selection_concept_filter("isActive")

# Only managers
filter = create_selection_concept_filter("isManager")
```

### 3. Using Filters in Batch Queries

```python
# Dimension member filters (focus on specific members)
dimension_member_filters = {
    "Function": ["Engineering", "Sales"],
    "Gender": ["Male", "Female"]  # Can still include multiple
}

# Global filters (apply to all metrics)
global_filters = [
    create_selection_concept_filter("isActive")
]

df = query_multiple_metrics(
    metric_ids=metric_ids,
    dimensions=["Function", "Gender"],
    dimension_member_filters=dimension_member_filters,
    global_filters=global_filters
)
```

## Complete Example

```python
from aggregate_query_vanilla import (
    query_multiple_metrics,
    create_selection_concept_filter
)

# Step 1: Define your 50 metrics
metric_ids = [
    "employeeCount",
    "turnoverRate",
    "headcount",
    "newHires",
    "terminations",
    # ... add 45 more
]

# Step 2: Define dimensions (2-3 work well)
dimensions = ["Function", "Gender"]

# Step 3: Define dimension member filters (optional)
# Focus on specific Functions
dimension_member_filters = {
    "Function": ["Engineering", "Sales", "Product"]
}

# Step 4: Define global filters (optional)
# Apply to all metrics
global_filters = [
    create_selection_concept_filter("isActive")  # Active employees only
]

# Step 5: Query all metrics
df = query_multiple_metrics(
    metric_ids=metric_ids,
    dimensions=dimensions,
    months=6,
    dimension_member_filters=dimension_member_filters,
    global_filters=global_filters,
    save_csv="all_50_metrics.csv"
)

# Step 6: Use the results
print(f"Retrieved {len(df)} rows")
print(f"Metrics: {[c for c in df.columns if c in metric_ids]}")
print(df.head())
```

## Output Format

The function returns a pandas DataFrame with:
- **Dimension columns**: Function, Gender, etc. (one per dimension)
- **Metric columns**: One column per metric_id (employeeCount, turnoverRate, etc.)
- **Time columns**: DateInRange (if time intervals are used)
- **Other columns**: Measures, support (if available)

Example output:
```
Function      Gender  DateInRange                    employeeCount  turnoverRate  headcount
Engineering   Male    2025-07-01T00:00:00.000Z - [0]  150.0         0.05         150.0
Engineering   Female  2025-07-01T00:00:00.000Z - [0]  75.0          0.03         75.0
Sales         Male    2025-07-01T00:00:00.000Z - [0]  200.0         0.08         200.0
...
```

## Performance Tips

1. **Use 2-3 dimensions**: More dimensions = more rows, slower queries
2. **Filter dimension members**: Focus on specific members to reduce data volume
3. **Use sparse results**: Set `options={"enableSparseResults": True}` to skip zero/null values
4. **Batch in groups**: If you have 100+ metrics, consider querying in batches of 50
5. **Progress tracking**: The function shows progress by default, which helps monitor long-running queries

## Error Handling

The function continues querying even if individual metrics fail:
- Failed metrics are logged but don't stop the batch
- The final DataFrame only includes successfully queried metrics
- Check the console output for any errors

## Finding Metric IDs

Use the metric discovery utility to find available metrics:

```bash
python metric_discovery.py --search headcount
python metric_discovery.py --object Employee
```

Or in Python:

```python
from metric_discovery import search_metrics, get_sdk_config
from visier_platform_sdk import ApiClient, Configuration

config = get_sdk_config()
api_client = ApiClient(config)

# Search for metrics
df = search_metrics(api_client, search_term="turnover")
print(df[["metric_id", "display_name"]])
```

## See Also

- `example_batch_query.py` - Working example script
- `VANILLA_AGGREGATE_USAGE.md` - Single metric query guide
- `AGGREGATE_QUERY_API_REFERENCE.md` - Full API reference
