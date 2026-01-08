#!/usr/bin/env python3
"""
Example: Batch Query Multiple Metrics

This example demonstrates how to query 50+ metrics efficiently with:
- Same dimensions (2-3 dimensions)
- Dimension member filtering (focus on specific members)
- Global filters (apply to all metrics)
"""

from aggregate_query_vanilla import (
    query_multiple_metrics,
    create_selection_concept_filter,
    create_member_set_filter
)

def main():
    print("=" * 70)
    print("Batch Query Example: Multiple Metrics with Filters")
    print("=" * 70)
    print()
    
    # Example: Query 50 metrics (using a few for demo)
    # In production, you'd have a list of 50 metric IDs
    metric_ids = [
        "employeeCount",
        "turnoverRate",
        "headcount",
        # ... add 47 more metrics here
    ]
    
    print(f"Querying {len(metric_ids)} metrics...")
    print("  Dimensions: Function, Gender")
    print("  Dimension filters: Only Engineering and Sales functions")
    print("  Global filter: Active employees only")
    print("  Time period: Last 6 months")
    print()
    
    # Query with:
    # - 2 dimensions: Function and Gender
    # - Dimension member filter: Only Engineering and Sales functions
    # - Global filter: Only active employees
    import os
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "batch_metrics_results.csv")
    
    df = query_multiple_metrics(
        metric_ids=metric_ids,
        dimensions=["Function", "Gender"],
        months=6,
        dimension_member_filters={
            "Function": ["Engineering", "Sales"]  # Only these functions
        },
        global_filters=[
            # Add global filters here (e.g., active employees only)
            # create_selection_concept_filter("isActive")
        ],
        save_csv=output_file
    )
    
    print()
    print("=" * 70)
    print("Results Summary")
    print("=" * 70)
    print(f"  Total rows: {len(df)}")
    print(f"  Columns: {', '.join(df.columns)}")
    print(f"  Metrics queried: {len([c for c in df.columns if c in metric_ids])}")
    print()
    
    # Show sample data
    print("Sample data (first 10 rows):")
    print(df.head(10).to_string(index=False))
    print()
    
    print("=" * 70)
    print("Tips for Production Use")
    print("=" * 70)
    print("1. Prepare your list of 50 metric IDs")
    print("2. Define your dimensions (2-3 dimensions work well)")
    print("3. Specify dimension member filters if you want to focus on specific members")
    print("4. Add global filters that apply to all metrics")
    print("5. The function will query all metrics and combine results")
    print("=" * 70)

if __name__ == "__main__":
    main()
