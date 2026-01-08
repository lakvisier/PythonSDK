# Aggregate Query API Reference

This document provides a reference for the full aggregate query API schema based on the official Visier API documentation.

## Query Structure

The aggregate query follows this structure:

```json
{
  "query": {
    "source": { ... },
    "axes": [ ... ],
    "filters": [ ... ],
    "timeIntervals": { ... },
    "parameterValues": [ ... ]
  },
  "options": { ... }
}
```

## Source

The `source` field defines what metric or formula to query:

```json
{
  "source": {
    "metric": "employeeCount",           // Predefined metric ID
    "formula": "string",                 // Custom formula (optional)
    "metrics": {                         // Multi-metric source (optional)
      "columns": [
        {
          "columnName": "string",
          "id": "string",
          "formula": "string",
          "qualifyingPath": "string"
        }
      ]
    }
  }
}
```

## Axes

Axes define how to group the data. **At least one axis is required for aggregate queries.**

### Dimension Level Selection (Most Common)

```json
{
  "axes": [
    {
      "dimensionLevelSelection": {
        "dimension": {
          "name": "Function",
          "qualifyingPath": "Employee"
        },
        "levelIds": ["Function"],
        "levelDepths": [0]  // Optional
      }
    }
  ]
}
```

### Other Axis Types

- **Selection Concept**: `{"selectionConcept": {"name": "isManager", "qualifyingPath": "Employee"}}`
- **Dimension Member Selection**: `{"dimensionMemberSelection": {...}}`
- **Member Map Selection**: `{"memberMapSelection": {...}}`
- **Numeric Ranges**: `{"numericRanges": {...}}`
- **Dimension Leaf Member Selection**: `{"dimensionLeafMemberSelection": {...}}`
- **Dimension Data Member Selection**: `{"dimensionDataMemberSelection": {...}}`
- **Formula**: `{"formula": "string"}`

### Axis Options

```json
{
  "tableAxisOptions": {
    "memberDisplayMode": "UNCHANGED",
    "columnName": "string"
  },
  "sortAndLimitOptions": {
    "sort": {
      "sortType": "CONFIGURED",
      "sortDirection": "SORT_ASCENDING"
    },
    "limit": {
      "limitType": "FIRST_N",
      "n": 0
    }
  }
}
```

## Filters

Filters define the population to query from:

### Selection Concept Filter

```json
{
  "filters": [
    {
      "selectionConcept": {
        "name": "isManager",
        "qualifyingPath": "Employee"
      }
    }
  ]
}
```

### Member Set Filter

```json
{
  "filters": [
    {
      "memberSet": {
        "dimension": {
          "name": "Function",
          "qualifyingPath": "Employee"
        },
        "values": {
          "included": [
            {
              "path": ["Engineering"],
              "memberId": "eng"
            }
          ],
          "excluded": [...]
        }
      }
    }
  ]
}
```

### Cohort Filter

```json
{
  "filters": [
    {
      "cohort": {
        "keyGroup": {
          "filters": [...]
        },
        "exclude": true,
        "timeInterval": {
          "intervalPeriodType": "MONTH",
          "intervalPeriodCount": 0,
          "direction": "BACKWARD",
          "shift": {...},
          "fromInstant": "string"
        }
      }
    }
  ]
}
```

### Formula Filter

```json
{
  "filters": [
    {
      "formula": "string"
    }
  ]
}
```

## Time Intervals

Time intervals define the time period to query. **Both `intervalCount` and `intervalPeriodCount` are valid.**

### Simple Dynamic Date

```json
{
  "timeIntervals": {
    "intervalCount": 3,
    "dynamicDateFrom": "SOURCE"  // or "COMPLETE_PERIOD"
  }
}
```

### Explicit Date Range

```json
{
  "timeIntervals": {
    "fromDateTime": "2021-01-01",      // ISO-8601 date
    "intervalPeriodType": "MONTH",     // MONTH, QUARTER, YEAR, etc.
    "intervalCount": 6                 // or "intervalPeriodCount": 6
  }
}
```

### With Direction and Shift

```json
{
  "timeIntervals": {
    "fromDateTime": "2021-01-01",
    "intervalPeriodType": "MONTH",
    "intervalCount": 6,
    "direction": "BACKWARD",           // or "FORWARD"
    "shift": {
      "periodType": "MONTH",
      "periodCount": 0,
      "direction": "BACKWARD"
    },
    "trailingPeriodType": "MONTH",
    "trailingPeriodCount": 0
  }
}
```

### From Instant (Epoch)

```json
{
  "timeIntervals": {
    "fromInstant": "1609459200000",    // Milliseconds since epoch
    "intervalPeriodType": "MONTH",
    "intervalCount": 6
  }
}
```

## Options

Query options control behavior and output format:

### Visibility Options

```json
{
  "options": {
    "zeroVisibility": "SHOW",          // or "HIDE" or "ELIMINATE"
    "nullVisibility": "SHOW",          // or "HIDE" or "ELIMINATE"
    "enableSparseResults": true        // Only return non-zero/non-null cells
  }
}
```

### Calendar and Currency

```json
{
  "options": {
    "calendarType": "TENANT_CALENDAR", // or "GREGORIAN_CALENDAR"
    "currencyConversionMode": "TENANT_CURRENCY_CONVERSION",
    "currencyConversionDate": "2021-01-01",
    "currencyConversionCode": "USD"
  }
}
```

### Display Options

```json
{
  "options": {
    "memberDisplayMode": "DEFAULT",    // or "COMPACT", "DISPLAY", "MDX", "COMPACT_DISPLAY"
    "axisVisibility": "SIMPLE",        // or "VERBOSE"
    "axesOverallValueMode": "NONE"     // or "AGGREGATE", "OVERALL"
  }
}
```

### Advanced Options

```json
{
  "options": {
    "lineageDepth": 0,
    "cellDistributionOptions": {
      "binCount": 0
    },
    "enableDescendingSpace": true,
    "internal": {
      "sparseHandlingMode": "ALLOW",
      "alignTimeAxisToPeriodEnd": true
    }
  }
}
```

## Parameter Values

For parameterized metrics, provide parameter values:

```json
{
  "parameterValues": [
    {
      "memberValue": {
        "parameterId": "string",
        "dimensionId": "string",
        "referencePath": ["string"],
        "values": {
          "included": [...],
          "excluded": [...]
        }
      }
    },
    {
      "numericValue": {
        "parameterId": "string",
        "value": 0.1
      }
    },
    {
      "planValue": {
        "parameterId": "string",
        "planId": "string",
        "scenarioId": "string",
        "snapshotId": "string"
      }
    }
  ]
}
```

## Complete Example

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
  },
  "options": {
    "zeroVisibility": "ELIMINATE",
    "nullVisibility": "ELIMINATE"
  }
}
```

## Notes

1. **Both `intervalCount` and `intervalPeriodCount` are valid** - the API accepts both field names
2. **At least one axis is required** - aggregate queries need at least one dimension for grouping
3. **Dimension format**: Always use `{"name": "...", "qualifyingPath": "..."}` format (not `objectName`)
4. **Time intervals are required** - queries must specify a time period
5. **Options are optional** - defaults work for most use cases

## References

- Official API Documentation: [Visier Data Query Aggregate Operation](https://docs.visier.com/visier-people/apis/references/api-reference.htm#tag/DataQuery/operation/DataQuery_Aggregate)
- Postman Collection: [Visier Alpine Platform Postman Collection](https://www.postman.com/visier-alpine/visier-alpine-platform/overview) - Interactive API examples and authentication flow
- SDK Examples: `visier-sdk-source/query_examples/aggregate/`
- SDK Tests: `visier-sdk-source/tests/integration/data/queries/aggregate.json`
