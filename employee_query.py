"""
Simple demo to query employee data from Visier Platform.

This script demonstrates:
- Basic authentication using environment variables
- Querying employee data for a specific time period (recent month)
- Retrieving specific properties: EmployeeID, Time_in_Role, Span_Of_Control

Usage:
    python employee_query.py

Environment variables (see visier.env.example):
    VISIER_HOST, VISIER_APIKEY, VISIER_VANITY (required)
    VISIER_USERNAME, VISIER_PASSWORD (required for Basic Auth)
"""

import sys
import warnings
import json
from datetime import datetime

warnings.filterwarnings('ignore', message='.*urllib3.*NotOpenSSLWarning.*')
warnings.filterwarnings('ignore', message='.*urllib3 v2 only supports OpenSSL.*')

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from visier_platform_sdk import ApiClient, Configuration, DataQueryApi, DataModelApi
from visier_platform_sdk.models import ListQueryExecutionDTO
from visier_platform_sdk.exceptions import (
    ServiceException, 
    ApiException, 
    BadRequestException,
    UnauthorizedException,
    ApiValueError
)

import os


def get_sdk_config():
    """
    Get SDK Configuration from environment variables.
    Uses Configuration.from_env() as recommended in the official SDK documentation.
    """
    # Use the recommended method from the SDK documentation
    return Configuration.from_env()


def get_recent_month_timestamp() -> str:
    """
    Get the timestamp for December 1, 2024 (known working date).
    Returns timestamp in milliseconds as string (Unix timestamp * 1000).
    """
    # Use December 1, 2024 - this date has data
    return "1735689600000"  # December 1, 2024


def build_query_dto():
    """
    Build a query DTO for employee data with EmployeeID, Time_in_Role, and Span_Of_Control.
    Uses fromInstant (timestamp) format for the recent month.
    """
    # Use December 1, 2024 timestamp (known working date)
    timestamp = get_recent_month_timestamp()
    
    query_dict = {
        "source": {"analyticObject": "Employee"},
        "columns": [
            {"columnName": "Employee ID", "columnDefinition": {"property": {"name": "Employee.EmployeeID", "qualifyingPath": "Employee"}}},
            {"columnName": "Time in Role", "columnDefinition": {"property": {"name": "Employee.Time_in_Role", "qualifyingPath": "Employee"}}},
            {"columnName": "Span of Control", "columnDefinition": {"property": {"name": "Employee.Span_Of_Control", "qualifyingPath": "Employee"}}}
        ],
        "timeInterval": {"fromInstant": timestamp},
        "options": {"limit": 10000, "page": 0}
    }
    
    # Convert dict to JSON string and create DTO
    json_string = json.dumps(query_dict)
    query_dto = ListQueryExecutionDTO.from_json(json_string)
    
    return query_dto


def convert_response_to_dataframe(response_dto):
    """
    Convert SDK response DTO to pandas DataFrame.
    Exact copy from getdata.py.
    """
    if response_dto is None:
        raise ValueError("Response is None - query may have returned no data or failed silently")
    
    # SDK may return DTO or dict depending on method used
    # Convert DTO to dict if needed
    if hasattr(response_dto, 'to_dict'):
        data = response_dto.to_dict()
    elif hasattr(response_dto, '__dict__'):
        # Try to convert DTO attributes to dict
        data = {}
        if hasattr(response_dto, 'header'):
            data['header'] = response_dto.header
        if hasattr(response_dto, 'rows'):
            data['rows'] = response_dto.rows
        # Check for other possible attributes
        for attr in ['data', 'result', 'response', 'body']:
            if hasattr(response_dto, attr):
                attr_val = getattr(response_dto, attr)
                if attr_val is not None:
                    data[attr] = attr_val
    else:
        # Assume it's already a dict
        data = response_dto
    
    if not data:
        raise ValueError("Response data is empty")
    
    header = data.get("header", {})
    rows = data.get("rows", [])
    
    if not rows:
        raise ValueError("No data rows found in response")
    
    # Create mapping from numeric keys to column names
    column_mapping = {
        str(k): header[str(k)] 
        for k in sorted([int(k) for k in header.keys()])
    }
    
    # Convert rows to list of dictionaries with proper column names
    df_rows = []
    for row in rows:
        df_row = {
            column_mapping.get(str(k), k): row.get(str(k))
            for k in sorted([int(k) for k in row.keys()])
        }
        df_rows.append(df_row)
    
    # Create DataFrame
    import pandas as pd
    df = pd.DataFrame(df_rows)
    
    # Reorder columns to match original header order
    column_order = [
        column_mapping[str(k)]
        for k in sorted([int(k) for k in header.keys()])
    ]
    df = df[column_order]
    
    return df


def display_results(df):
    """
    Display query results in a simple table format.
    """
    if df is None or df.empty:
        print("\nNo data returned from query.")
        return
    
    print("\n" + "=" * 70)
    print("Query Results")
    print("=" * 70)
    print(f"\nFound {len(df)} employee record(s):\n")
    
    # Display first 20 rows
    print(df.head(20).to_string(index=False))
    
    if len(df) > 20:
        print(f"\n... and {len(df) - 20} more rows")
    
    print()


def main():
    """
    Main function to run the demo.
    """
    print("=" * 70)
    print("Visier Employee Data Query Demo")
    print("=" * 70)
    print()
    
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
        return
    
    try:
        # Step 1: Create client (authentication happens automatically on first API call)
        print("Step 1: Creating API client...")
        sdk_config = get_sdk_config()
        # Set as default configuration (recommended in SDK docs)
        Configuration.set_default(sdk_config)
        api_client = ApiClient(sdk_config)
        print("✓ API client created")
        print("  (Authentication will happen automatically on first API call)")
        print()
        
        # Step 2: Build query
        data_query_api = DataQueryApi(api_client)
        print("Step 2: Building query...")
        timestamp = get_recent_month_timestamp()
        first_day = datetime(2024, 12, 1).strftime("%Y-%m-%d")
        print(f"  Time period: From {first_day} (December 2024)")
        print("  Analytic Object: Employee")
        print("  Properties: EmployeeID, Time_in_Role, Span_Of_Control")
        query_dto = build_query_dto()
        print("✓ Query built")
        print()
        
        # Step 3: Execute query (exact pattern from getdata.py)
        print("Step 3: Executing query...")
        try:
            response = data_query_api.list(query_dto)
            if response is None:
                print("  ⚠ Warning: Response is None")
                print("  This may indicate:")
                print("    - No data available for the specified time period")
                print("    - Properties don't exist in your tenant")
                print("    - Query format issue")
                print("\n  Trying to inspect response object...")
                # Try to get more info about what was returned
                return
        except ServiceException as e:
            print(f"\n⚠ SDK returned server error (500). This might be a query format issue.", file=sys.stderr)
            print(f"Error code: {e.data.get('code', 'Unknown') if hasattr(e, 'data') and e.data else 'Unknown'}", file=sys.stderr)
            print(f"RCI: {e.data.get('rci', 'Unknown') if hasattr(e, 'data') and e.data else 'Unknown'}", file=sys.stderr)
            raise
        except ApiException as e:
            print(f"\n⚠ API error occurred: {e}", file=sys.stderr)
            if hasattr(e, 'body'):
                print(f"Response body: {e.body}", file=sys.stderr)
            raise
        
        print("✓ Query executed successfully")
        if response:
            print(f"  Response type: {type(response)}")
            if hasattr(response, '__dict__'):
                print(f"  Response attributes: {list(response.__dict__.keys())[:10]}")
        print()
        
        # Step 4: Process and display results
        print("Step 4: Processing results...")
        df = convert_response_to_dataframe(response)
        display_results(df)
        
        print("=" * 70)
        print("Demo completed successfully!")
        print(f"  Shape: {df.shape[0]} rows, {df.shape[1]} columns")
        print("=" * 70)
        
    except ApiValueError as e:
        print(f"\n✗ Configuration error: {e}")
        print("\nPlease ensure your .env file contains all required variables:")
        print("  - VISIER_HOST")
        print("  - VISIER_APIKEY")
        print("  - VISIER_VANITY")
        print("  - VISIER_USERNAME")
        print("  - VISIER_PASSWORD")
        return
    except UnauthorizedException as e:
        print(f"\n✗ Authentication failed: {e}")
        print("\nPlease verify your credentials in the .env file")
        return
    except BadRequestException as e:
        print(f"\n✗ Bad request: {e}")
        if hasattr(e, 'body'):
            print(f"  Details: {e.body}")
        print("\nThis may indicate:")
        print("  - Invalid query format")
        print("  - Properties don't exist in your tenant")
        print("  - Missing required query parameters")
        return
    except ValueError as e:
        print(f"\n✗ Error: {e}")
        print("\nThis usually means:")
        print("  - No data was returned for the specified time period")
        print("  - The properties may not exist in your tenant")
        print("  - You may not have permissions to access this data")
        return
    except ServiceException as e:
        print(f"\n✗ Server error: {e.status} - {e.reason}")
        if hasattr(e, 'data') and e.data:
            print(f"  Error code: {e.data.get('code', 'Unknown')}")
            print(f"  RCI: {e.data.get('rci', 'Unknown')}")
        return
    except ApiException as e:
        print(f"\n✗ API Error: {e.status} - {e.reason}")
        if hasattr(e, 'body'):
            print(f"  Details: {e.body}")
        return
    except ImportError as e:
        print(f"✗ Error: {e}")
        print("\nPlease install required packages:")
        print("  pip install visier-platform-sdk pandas")
        return
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return


if __name__ == "__main__":
    main()
