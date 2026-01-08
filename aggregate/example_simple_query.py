#!/usr/bin/env python3
"""
Simple Example: Querying Visier Metrics

This example demonstrates the simplest way to query Visier metrics
using the query_metric() function.
"""

from aggregate_query_vanilla import query_metric

def main():
    print("=" * 70)
    print("Simple Visier Metric Query Example")
    print("=" * 70)
    print()
    
    # Example 1: Employee count by Function (last 6 months)
    print("Example 1: Employee count by Function")
    print("-" * 70)
    df1 = query_metric(
        metric_id="employeeCount",
        dimensions=["Function"],
        months=6
    )
    print(f"✓ Retrieved {len(df1)} rows")
    print(f"  Total employees: {df1['value'].sum():.0f}")
    print()
    
    # Example 2: Employee count by Function and Pay Level (save to CSV)
    print("Example 2: Employee count by Function and Pay Level")
    print("-" * 70)
    import os
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "employee_by_function_paylevel.csv")
    
    df2 = query_metric(
        metric_id="employeeCount",
        dimensions=["Function", "Pay_Level"],
        months=6,
        save_csv=output_file
    )
    print(f"✓ Retrieved {len(df2)} rows")
    print(f"  Saved to: {output_file}")
    print()
    
    # Example 3: Last 12 months
    print("Example 3: Employee count by Function (last 12 months)")
    print("-" * 70)
    df3 = query_metric(
        metric_id="employeeCount",
        dimensions=["Function"],
        months=12
    )
    print(f"✓ Retrieved {len(df3)} rows")
    print(f"  Total employees: {df3['value'].sum():.0f}")
    print()
    
    print("=" * 70)
    print("All examples completed successfully!")
    print("=" * 70)
    print()
    print("💡 Try modifying the queries:")
    print("   - Change dimensions: ['Gender'], ['Location'], etc.")
    print("   - Change time period: months=3, months=24")
    print("   - Try different metrics: 'applicantCount', etc.")
    print()

if __name__ == "__main__":
    main()
