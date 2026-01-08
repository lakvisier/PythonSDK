# Aggregate Query Implementation Plan for Predefined Metrics

## Overview
This document outlines the plan for implementing aggregate queries for predefined metrics using the Visier Python SDK, based on analysis of the `visier-sdk-source` repository.

## Key Findings from SDK Source Analysis

### 1. Query Structure

Aggregate queries use a different structure than list queries:

**List Query** (current implementation):
- Uses `ListQueryExecutionDTO`
- Source: `{"analyticObject": "Employee"}`
- Columns: Array of property definitions
- Returns: `ListResponse` with rows and header

**Aggregate Query** (to implement):
- Uses `AggregationQueryExecutionDTO`
- Source: `{"metric": "metricId"}` (predefined metric ID)
- Axes: Array of dimension level selections (for grouping)
- Filters: Array of selection concepts (for filtering)
- Time Intervals: Time period specification
- Returns: `CellSetDTO` with cells and axes

### 2. Example Query Structures

**Example 1: Simple query with dynamic date** (from [Visier API Documentation](https://docs.visier.com/visier-people/apis/references/api-reference.htm#tag/DataQuery/operation/DataQuery_Aggregate)):

```json
{
  "query": {
    "source": {
      "metric": "employeeCount"
    },
    "timeIntervals": {
      "intervalCount": 3,
      "dynamicDateFrom": "SOURCE"
    },
    "axes": [
      {
        "dimension": {
          "name": "Gender"
        }
      }
    ]
  }
}
```

**Example 2: Complex query with filters** (from SDK test files):

```json
{
  "query": {
    "source": {
      "metric": "employeeCount"
    },
    "axes": [
      {
        "dimensionLevelSelection": {
          "dimension": {
            "name": "Function",
            "qualifyingPath": "Employee"
          },
          "levelIds": ["Function"]
        }
      },
      {
        "dimensionLevelSelection": {
          "dimension": {
            "name": "Pay_Level",
            "qualifyingPath": "Employee"
          },
          "levelIds": ["Pay_Level"]
        }
      }
    ],
    "filters": [
      {
        "selectionConcept": {
          "name": "isManager",
          "qualifyingPath": "Employee"
        }
      }
    ],
    "timeIntervals": {
      "fromDateTime": "2021-01-01",
      "intervalPeriodType": "MONTH",
      "intervalCount": 6
    }
  }
}
```

**Key Observations:**
- Axes can be simplified: `{"dimension": {"name": "Gender"}}` OR full structure with `dimensionLevelSelection`
- Time intervals support multiple formats:
  - `dynamicDateFrom: "SOURCE"` with `intervalCount` (simpler, relative to data)
  - `fromDateTime` with `intervalPeriodType` and `intervalCount` (absolute date)

### 3. API Method

```python
from visier_platform_sdk import DataQueryApi
from visier_platform_sdk.models import AggregationQueryExecutionDTO

data_query_api = DataQueryApi(api_client)
response = data_query_api.aggregate(aggregation_query_dto)
# Returns: CellSetOrErrorDTO (which contains CellSetDTO or error)
# Access: response.cell_set (if successful) or response.error (if failed)
```

**Endpoint**: `POST /v1/data/query/aggregate`  
**Reference**: [Visier API Documentation](https://docs.visier.com/visier-people/apis/references/api-reference.htm#tag/DataQuery/operation/DataQuery_Aggregate)

### 4. Response Structure

`CellSetDTO` contains:
- `cells`: List of `CellDTO` objects with metric values
- `axes`: List of `CellSetAxisDTO` objects representing dimension groupings
- `lineage`: Optional lineage information

## Implementation Plan

### Phase 1: Basic Aggregate Query Function
**Goal**: Create a function to execute a simple aggregate query for a predefined metric

**Steps**:
1. Create `aggregate_query.py` script
2. Implement function to build `AggregationQueryExecutionDTO` from dict
3. Implement function to execute aggregate query
4. Implement function to convert `CellSetDTO` to pandas DataFrame
5. Add example using `employeeCount` metric

**Key Components**:
- `build_aggregate_query_dto(metric_id, axes=None, filters=None, time_intervals=None)`
- `execute_aggregate_query(query_dto)`
- `convert_cellset_to_dataframe(cell_set_dto)`

### Phase 2: Metric Discovery
**Goal**: Help users discover available predefined metrics

**Steps**:
1. Research MetricsV2Api for listing available metrics
2. Create utility function to list available metrics
3. Add filtering/search capabilities

**Key Components**:
- `list_available_metrics(analytic_object=None)`
- `search_metrics(search_term)`

### Phase 3: Enhanced Query Builder
**Goal**: Create a more user-friendly query builder with helper functions

**Steps**:
1. Create helper functions for common query patterns
2. Add validation for metric IDs
3. Add support for multiple metrics
4. Add support for formulas (ad-hoc metrics)

**Key Components**:
- `build_metric_query(metric_id, ...)`
- `build_formula_query(formula, ...)`
- `add_dimension_axis(dimension_name, qualifying_path, level_ids)`
- `add_concept_filter(concept_name, qualifying_path)`

### Phase 4: Response Processing
**Goal**: Create utilities to process and analyze CellSet responses

**Steps**:
1. Create DataFrame conversion with proper axis handling
2. Add pivot table conversion for multi-dimensional results
3. Add visualization helpers
4. Add export capabilities (CSV, Excel)

**Key Components**:
- `cellset_to_dataframe(cell_set, pivot=False)`
- `cellset_to_pivot_table(cell_set)`
- `visualize_cellset(cell_set, chart_type='bar')`

### Phase 5: Documentation and Examples
**Goal**: Create comprehensive documentation and examples

**Steps**:
1. Update README with aggregate query examples
2. Create Jupyter notebook section for aggregate queries
3. Add example queries for common metrics
4. Document common patterns and use cases

## File Structure

```
PythonSDK/
├── aggregate_query.py              # Main aggregate query implementation
├── metric_discovery.py             # Utility for discovering metrics
├── aggregate_query_examples.py     # Example queries
├── aggregate_query_walkthrough.ipynb  # Jupyter notebook tutorial
└── AGGREGATE_QUERY_PLAN.md         # This file
```

## Key Differences: List vs Aggregate Queries

| Aspect | List Query | Aggregate Query |
|--------|-----------|-----------------|
| **Purpose** | Get detailed records | Get aggregated summaries |
| **Source** | Analytic Object | Metric ID |
| **Columns** | Properties | N/A (uses metric) |
| **Grouping** | N/A | Axes (dimensions) |
| **Response** | ListResponse (rows) | CellSetDTO (cells) |
| **Use Case** | "Show me all employees" | "Show me headcount by department" |

## Common Metrics (Examples)

Based on SDK examples:
- `employeeCount` - Total employee count
- `applicantCount` - Total applicant count

(Note: Actual metric IDs depend on your Visier tenant configuration)

## Next Steps

1. **Start with Phase 1**: Implement basic aggregate query functionality
2. **Test with known metrics**: Use `employeeCount` or similar
3. **Iterate**: Add features based on user needs
4. **Document**: Keep examples and documentation updated

## Issues & Discrepancies Found

### 1. Response Type Discrepancy
- **API Signature**: `aggregate()` returns `CellSetOrErrorDTO` (which contains either `cellSet` or `error`)
- **Test Code**: Accesses `cell_set_dto.axes` and `cell_set_dto.cells` directly, suggesting it's `CellSetDTO`
- **Resolution Needed**: Verify if the API unwraps automatically or if we need to check `response.cell_set` vs `response.error`

### 2. Time Interval Field Names - RESOLVED
- **`intervalCount`**: Number of periods to include (e.g., 3 months)
- **`intervalPeriodCount`**: Appears to be an alternative/legacy field name
- **`dynamicDateFrom`**: Can be set to `"SOURCE"` to automatically determine start date from available data
- **`fromDateTime`**: Explicit start date (ISO-8601 format: `"2021-01-01"`)
- **`intervalPeriodType`**: Type of period (`"MONTH"`, `"QUARTER"`, `"YEAR"`, etc.)
- **Resolution**: Use `intervalCount` with either `dynamicDateFrom: "SOURCE"` (simpler) OR `fromDateTime` + `intervalPeriodType` (explicit)

### 3. Query Options - DOCUMENTED
The `options` field in `AggregationQueryExecutionDTO` supports:
- **`zeroVisibility`**: `"SHOW"`, `"HIDE"`, or `"ELIMINATE"` (default: `"SHOW"`)
- **`nullVisibility`**: `"SHOW"`, `"HIDE"`, or `"ELIMINATE"` (default: `"SHOW"`)
- **`memberDisplayMode`**: `"DEFAULT"`, `"COMPACT"`, `"DISPLAY"`, `"MDX"`, `"COMPACT_DISPLAY"` (default: `"DEFAULT"`)
- **`axesOverallValueMode`**: `"NONE"`, `"AGGREGATE"`, `"OVERALL"` (default: `"NONE"`)
- **`axisVisibility`**: `"SIMPLE"` or `"VERBOSE"` (default: `"SIMPLE"`)
- **`enableSparseResults`**: Boolean - only return non-zero/non-null cells
- **`calendarType`**: `"TENANT_CALENDAR"` or `"GREGORIAN_CALENDAR"` (default: `"TENANT_CALENDAR"`)
- Options are **optional** - defaults work for most use cases

## Questions to Resolve

1. **Response Handling**: The API returns `CellSetOrErrorDTO`. We need to check:
   - `response.cell_set` if successful (contains `CellSetDTO`)
   - `response.error` if failed (contains `QueryExecutionErrorDTO`)
   - **Action**: Implement proper error checking and unwrapping

2. **Metric Discovery**: How do you want to discover available metrics in your tenant?
   - Use MetricsV2Api to list all metrics?
   - Hardcode common metric IDs?
   - Provide a utility function to search/browse?

3. **Use Cases**: What specific aggregate queries do you need?
   - Simple metric queries (e.g., "total headcount")?
   - Grouped by dimensions (e.g., "headcount by department")?
   - Filtered queries (e.g., "headcount for managers only")?
   - Time series (e.g., "headcount over 6 months")?

4. **Metric IDs**: Do you know the exact metric IDs in your tenant, or do we need to discover them first?

5. **Output Format**: How do you want to consume the results?
   - Simple DataFrame (flattened)?
   - Pivot table format?
   - Raw CellSet structure?
   - Visualization-ready format?

6. **Error Handling**: How should we handle query errors? Show error details, retry logic, etc.?

7. **Axes Structure**: Should we support both simplified axes (`{"dimension": {"name": "Gender"}}`) and full structure (`dimensionLevelSelection`)? Or start with one?

## References

- **Official API Documentation**: [Visier Data Query Aggregate Operation](https://docs.visier.com/visier-people/apis/references/api-reference.htm#tag/DataQuery/operation/DataQuery_Aggregate)
- **SDK Source**: `visier-sdk-source/`
- **Example Queries**: `visier-sdk-source/query_examples/aggregate/`
- **Integration Tests**: `visier-sdk-source/tests/integration/test_data_query_api.py`
- **API Implementation**: `visier-sdk-source/src/visier_platform_sdk/visier_platform_sdk/api/data_query_api.py`
- **Model Definitions**: `visier-sdk-source/src/visier_platform_sdk/visier_platform_sdk/models/`
