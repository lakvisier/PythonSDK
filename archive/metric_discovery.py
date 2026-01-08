"""
Metric Discovery Utility for Visier Predefined Metrics

This script helps you discover available predefined metrics in your Visier tenant.
It uses the MetricsV2Api to list all predefined metrics (both simple and derived).

Usage:
    python metric_discovery.py                    # List all metrics
    python metric_discovery.py --object Employee  # List metrics for Employee object
    python metric_discovery.py --search headcount # Search for metrics containing "headcount"
"""

import sys
import warnings
import argparse
from typing import Optional, List

warnings.filterwarnings('ignore', message='.*urllib3.*NotOpenSSLWarning.*')
warnings.filterwarnings('ignore', message='.*urllib3 v2 only supports OpenSSL.*')

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from visier_platform_sdk import ApiClient, Configuration, MetricsV2Api
from visier_platform_sdk.exceptions import (
    ServiceException,
    ApiException,
    BadRequestException,
    UnauthorizedException,
    ApiValueError
)

import os
import pandas as pd


def get_sdk_config():
    """Get SDK Configuration from environment variables."""
    return Configuration.from_env()


def list_all_metrics(
    api_client: ApiClient,
    metric_type: Optional[List[str]] = None,
    include_details: bool = False
) -> pd.DataFrame:
    """
    List all predefined metrics in the tenant.
    
    Args:
        api_client: The API client
        metric_type: Optional list of types to filter by: ['simple'] or ['derived'] or None for all
        include_details: If True, includes additional details about metrics
    
    Returns:
        DataFrame with metric information
    """
    metrics_api = MetricsV2Api(api_client)
    
    # Build var_with parameter
    var_with = ['details'] if include_details else ['basic']
    
    # Get all metrics
    response = metrics_api.get_all_metrics(
        type=metric_type,
        var_with=var_with
    )
    
    # Extract metrics from response
    # Response structure: MetricResponseDTO.metrics -> List[MetricWithContextDTO]
    # Each MetricWithContextDTO has: .metric -> MetricDefinitionDTO
    # MetricDefinitionDTO has: .object_name, .basic_information (display_name, description), .details (metric_type)
    metrics = []
    if hasattr(response, 'metrics') and response.metrics:
        for metric_with_context in response.metrics:
            # Access the nested metric definition
            metric_def = getattr(metric_with_context, 'metric', None) if metric_with_context else None
            
            if metric_def:
                # Get basic information
                basic_info = getattr(metric_def, 'basic_information', None)
                details = getattr(metric_def, 'details', None)
                
                # Extract metric type from details
                metric_type = None
                if details:
                    metric_type = getattr(details, 'metric_type', None)
                
                metric_info = {
                    'Metric ID': getattr(metric_def, 'object_name', None),
                    'Display Name': getattr(basic_info, 'display_name', None) if basic_info else None,
                    'Type': metric_type,
                    'Description': getattr(basic_info, 'description', None) if basic_info else None,
                }
                
                # Add additional details if requested
                if include_details:
                    metric_info['UUID'] = getattr(metric_def, 'uuid', None)
                    metric_info['Visible in Analytics'] = getattr(metric_def, 'visible_in_analytics', None)
                    metric_info['Analytic Object'] = getattr(metric_def, 'analytic_object_name', None)
                
                metrics.append(metric_info)
    
    return pd.DataFrame(metrics)


def list_analytic_object_metrics(
    api_client: ApiClient,
    analytic_object_name: str,
    metric_type: Optional[List[str]] = None,
    include_details: bool = False
) -> pd.DataFrame:
    """
    List predefined metrics for a specific analytic object.
    
    Args:
        api_client: The API client
        analytic_object_name: Name of the analytic object (e.g., "Employee", "Applicant")
        metric_type: Optional list of types to filter by: ['simple'] or ['derived'] or None for all
        include_details: If True, includes additional details about metrics
    
    Returns:
        DataFrame with metric information
    """
    metrics_api = MetricsV2Api(api_client)
    
    # Build var_with parameter
    var_with = ['details'] if include_details else ['basic']
    
    # Get metrics for the analytic object
    response = metrics_api.get_analytic_object_metrics(
        analytic_object_name=analytic_object_name,
        type=metric_type,
        var_with=var_with
    )
    
    # Extract metrics from response
    # Response structure: MetricResponseDTO.metrics -> List[MetricWithContextDTO]
    # Each MetricWithContextDTO has: .metric -> MetricDefinitionDTO
    # MetricDefinitionDTO has: .object_name, .basic_information (display_name, description), .details (metric_type)
    metrics = []
    if hasattr(response, 'metrics') and response.metrics:
        for metric_with_context in response.metrics:
            # Access the nested metric definition
            metric_def = getattr(metric_with_context, 'metric', None) if metric_with_context else None
            
            if metric_def:
                # Get basic information
                basic_info = getattr(metric_def, 'basic_information', None)
                details = getattr(metric_def, 'details', None)
                
                # Extract metric type from details
                metric_type = None
                if details:
                    metric_type = getattr(details, 'metric_type', None)
                
                metric_info = {
                    'Metric ID': getattr(metric_def, 'object_name', None),
                    'Display Name': getattr(basic_info, 'display_name', None) if basic_info else None,
                    'Type': metric_type,
                    'Description': getattr(basic_info, 'description', None) if basic_info else None,
                }
                
                # Add additional details if requested
                if include_details:
                    metric_info['UUID'] = getattr(metric_def, 'uuid', None)
                    metric_info['Visible in Analytics'] = getattr(metric_def, 'visible_in_analytics', None)
                    metric_info['Analytic Object'] = getattr(metric_def, 'analytic_object_name', None)
                
                metrics.append(metric_info)
    
    return pd.DataFrame(metrics)


def search_metrics(df: pd.DataFrame, search_term: str) -> pd.DataFrame:
    """
    Search for metrics by name or description.
    
    Args:
        df: DataFrame with metrics
        search_term: Search term to match against metric IDs, display names, or descriptions
    
    Returns:
        Filtered DataFrame
    """
    if df.empty:
        return df
    
    search_term_lower = search_term.lower()
    
    # Search across multiple columns
    mask = (
        df['Metric ID'].astype(str).str.lower().str.contains(search_term_lower, na=False) |
        df['Display Name'].astype(str).str.lower().str.contains(search_term_lower, na=False) |
        df['Description'].astype(str).str.lower().str.contains(search_term_lower, na=False)
    )
    
    return df[mask]


def display_metrics(df: pd.DataFrame, title: str = "Available Predefined Metrics"):
    """Display metrics in a formatted table."""
    if df.empty:
        print(f"\n⚠ No metrics found.")
        return
    
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)
    print(f"\nFound {len(df)} predefined metric(s):\n")
    
    # Display in a clean format
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', 50)
    
    print(df.to_string(index=False))
    
    print("\n" + "=" * 80)
    print("\n💡 Usage:")
    print("   Use the 'Metric ID' value in your aggregate queries:")
    print("   Example: build_aggregate_query_dto(metric_id='employeeCount', ...)")
    print("=" * 80)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Discover predefined metrics in your Visier tenant',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python metric_discovery.py
  python metric_discovery.py --object Employee
  python metric_discovery.py --type simple
  python metric_discovery.py --search headcount
  python metric_discovery.py --object Employee --details
        """
    )
    parser.add_argument(
        '--object',
        dest='analytic_object',
        help='Filter metrics by analytic object (e.g., Employee, Applicant)'
    )
    parser.add_argument(
        '--type',
        choices=['simple', 'derived'],
        help='Filter by metric type (simple or derived)'
    )
    parser.add_argument(
        '--search',
        help='Search for metrics containing this term'
    )
    parser.add_argument(
        '--details',
        action='store_true',
        help='Include additional details (UUID, visibility, etc.)'
    )
    
    args = parser.parse_args()
    
    # Check required environment variables
    required_vars = [
        "VISIER_HOST",
        "VISIER_APIKEY",
        "VISIER_VANITY",
        "VISIER_USERNAME",
        "VISIER_PASSWORD"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print("Error: Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these in your .env file or environment.")
        print("See visier.env.example for a template.")
        return 1
    
    try:
        # Create API client
        print("Connecting to Visier...")
        sdk_config = get_sdk_config()
        Configuration.set_default(sdk_config)
        api_client = ApiClient(sdk_config)
        print("✓ Connected\n")
        
        # Determine metric type filter
        metric_type = [args.type] if args.type else None
        
        # Get metrics
        if args.analytic_object:
            print(f"Fetching predefined metrics for '{args.analytic_object}'...")
            df = list_analytic_object_metrics(
                api_client,
                args.analytic_object,
                metric_type=metric_type,
                include_details=args.details
            )
            title = f"Predefined Metrics for {args.analytic_object}"
        else:
            print("Fetching all predefined metrics...")
            df = list_all_metrics(
                api_client,
                metric_type=metric_type,
                include_details=args.details
            )
            title = "All Predefined Metrics"
        
        # Apply search filter if provided
        if args.search:
            print(f"Searching for '{args.search}'...")
            df = search_metrics(df, args.search)
            title += f" (matching '{args.search}')"
        
        # Display results
        display_metrics(df, title)
        
        return 0
        
    except ApiValueError as e:
        print(f"\n✗ Configuration error: {e}")
        return 1
    except UnauthorizedException as e:
        print(f"\n✗ Authentication failed: {e}")
        return 1
    except BadRequestException as e:
        print(f"\n✗ Bad request: {e}")
        if hasattr(e, 'body'):
            print(f"  Details: {e.body}")
        return 1
    except ServiceException as e:
        print(f"\n✗ Server error: {e.status} - {e.reason}")
        return 1
    except ApiException as e:
        print(f"\n✗ API Error: {e.status} - {e.reason}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
