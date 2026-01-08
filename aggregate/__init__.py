"""
Visier Aggregate Query Module

This module provides a simple, RESTful API-based interface for querying
aggregate metrics from Visier without SDK dependencies.

Quick Start:
    from aggregate.aggregate_query_vanilla import query_metric
    
    df = query_metric("employeeCount", dimensions=["Function"])
"""

__version__ = "1.0.0"
