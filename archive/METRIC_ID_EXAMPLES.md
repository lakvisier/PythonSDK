# Metric ID Examples from SDK

This document lists metric IDs found in the Visier SDK source code and examples.

## Metric IDs Found in SDK Examples

### 1. `employeeCount`
**Location**: Multiple examples
- **File**: `visier-sdk-source/tests/integration/data/queries/aggregate.json`
- **File**: `visier-sdk-source/tests/integration/test_data_query_api.py` (SQL-like query)
- **File**: `visier-sdk-source/query_examples/sql-like/aggregate/employee-count.sql`

**Usage Examples**:

**Aggregate Query (JSON)**:
```json
{
  "query": {
    "source": {
      "metric": "employeeCount"
    }
  }
}
```

**SQL-like Query**:
```sql
SELECT employeeCount() AS "Headcount", Union_Status FROM Employee
```

**Note**: In SQL-like queries, metrics are called as functions with parentheses: `employeeCount()`

### 2. `applicantCount`
**Location**: `visier-sdk-source/query_examples/aggregate/applicants-source.json`

**Usage Example**:
```json
{
  "query": {
    "source": {
      "metric": "applicantCount"
    },
    "axes": [
      {
        "dimensionLevelSelection": {
          "dimension": {
            "name": "Application_Source",
            "qualifyingPath": "Applicant"
          },
          "levelIds": ["Application_Source"]
        }
      }
    ]
  }
}
```

## Important Notes

1. **Metric IDs are tenant-specific**: The actual metric IDs available in your tenant may differ from these examples.

2. **Case sensitivity**: Metric IDs appear to be case-sensitive. Examples use camelCase (`employeeCount`, `applicantCount`).

3. **Display names vs IDs**: 
   - **Metric ID**: `employeeCount` (used in API calls)
   - **Display Name**: "Headcount" (shown in UI)
   - The SDK documentation shows that `employeeCount` has display name "Headcount"

4. **Finding metrics in your tenant**:
   - Use the **MetricsV2Api** to list available metrics
   - Use the **SearchApi** to search for metrics by name
   - Check your Visier tenant's metric catalog in the UI

## Common Metric Patterns

Based on SDK examples and documentation:

- **Count metrics**: `employeeCount`, `applicantCount`
- **Rate metrics**: `turnoverRate` (mentioned in search examples)
- **Ratio metrics**: `employeeRatio` (mentioned in search examples)

## How to Discover Metrics in Your Tenant

### Option 1: Use MetricsV2Api (Recommended)
```python
from visier_platform_sdk import MetricsV2Api

metrics_api = MetricsV2Api(api_client)
# List all metrics
metrics = metrics_api.get_metrics()
```

### Option 2: Use SearchApi
```python
from visier_platform_sdk import SearchApi

search_api = SearchApi(api_client)
# Search for metrics containing "headcount"
results = search_api.search_visier_objects(
    query=["headcount"],
    object_type="METRIC"
)
```

### Option 3: Check Visier UI
- Navigate to your Visier tenant
- Go to Metrics/Reports section
- Check the metric catalog
- Note the metric IDs (often shown in tooltips or metadata)

## References

- **SDK Test Files**: `visier-sdk-source/tests/integration/data/queries/aggregate.json`
- **Query Examples**: `visier-sdk-source/query_examples/aggregate/`
- **SQL Examples**: `visier-sdk-source/query_examples/sql-like/aggregate/`
- **Model Documentation**: `visier-sdk-source/src/visier_platform_sdk/visier_platform_sdk/models/metric_validation_summary_dto.py`
