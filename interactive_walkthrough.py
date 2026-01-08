"""
Interactive Walkthrough: Visier Python SDK

This interactive script educates users on how to use the Visier Python SDK
to query employee data. It walks through each step with explanations and
allows users to proceed at their own pace.

Usage:
    python interactive_walkthrough.py
"""

import sys
import warnings
from datetime import datetime
import time
from typing import Optional

warnings.filterwarnings('ignore', message='.*urllib3.*NotOpenSSLWarning.*')
warnings.filterwarnings('ignore', message='.*urllib3 v2 only supports OpenSSL.*')

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from visier_platform_sdk import ApiClient, Configuration, DataQueryApi
from visier_platform_sdk.models import ListQueryExecutionDTO, ListResponse
from visier_platform_sdk.exceptions import (
    ServiceException, 
    ApiException, 
    BadRequestException,
    UnauthorizedException,
    ApiValueError
)

import os


def print_section(title, description=""):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)
    if description:
        print(f"\n{description}\n")


def print_step(step_num, title, description=""):
    """Print a formatted step."""
    print(f"\n{'─' * 70}")
    print(f"STEP {step_num}: {title}")
    print(f"{'─' * 70}")
    if description:
        print(f"\n{description}\n")


def wait_for_user(prompt="Press Enter to continue..."):
    """Wait for user to press Enter."""
    input(f"\n{prompt}")


def print_code_explanation(code, explanation):
    """Print code with explanation."""
    print(f"\n📝 Code:")
    print(f"   {code}")
    print(f"\n💡 Explanation:")
    print(f"   {explanation}")


def get_sdk_config():
    """Get SDK Configuration from environment variables."""
    return Configuration.from_env()


def get_timestamp() -> str:
    """Get timestamp for December 1, 2024 (working date)."""
    return "1735689600000"  # December 1, 2024


def build_query_dto() -> ListQueryExecutionDTO:
    """Build a query DTO for employee data."""
    timestamp = get_timestamp()
    
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
    
    # Use from_dict() instead of from_json() - simpler and more direct
    query_dto = ListQueryExecutionDTO.from_dict(query_dict)
    
    return query_dto


def convert_response_to_dataframe(response: ListResponse):
    """
    Convert SDK ListResponse to pandas DataFrame.
    
    The SDK's list() method returns a ListResponse object which is a Pydantic model
    with 'header' and 'rows' attributes. We access them directly to avoid Pydantic
    serialization warnings.
    """
    if response is None:
        raise ValueError("Response is None")
    
    # Access attributes directly to avoid Pydantic serialization warnings
    # header and rows are Any types but are typically dicts in practice
    header = response.header
    rows = response.rows
    
    # Convert to dict if they're Pydantic models, otherwise use as-is
    if header is not None and hasattr(header, 'to_dict'):
        header = header.to_dict()
    elif header is None:
        header = {}
    
    if rows is None:
        rows = []
    elif rows and hasattr(rows[0], 'to_dict'):
        rows = [row.to_dict() if hasattr(row, 'to_dict') else row for row in rows]
    
    if not rows:
        raise ValueError("No data rows found in response")
    
    column_mapping = {
        str(k): header[str(k)] 
        for k in sorted([int(k) for k in header.keys()])
    }
    
    df_rows = []
    for row in rows:
        df_row = {
            column_mapping.get(str(k), k): row.get(str(k))
            for k in sorted([int(k) for k in row.keys()])
        }
        df_rows.append(df_row)
    
    import pandas as pd
    df = pd.DataFrame(df_rows)
    
    column_order = [
        column_mapping[str(k)]
        for k in sorted([int(k) for k in header.keys()])
    ]
    df = df[column_order]
    
    return df


def display_results(df, limit=10):
    """Display query results."""
    if df is None or df.empty:
        print("\nNo data returned from query.")
        return
    
    print("\n" + "=" * 70)
    print("Query Results")
    print("=" * 70)
    print(f"\nFound {len(df)} employee record(s):\n")
    
    print(df.head(limit).to_string(index=False))
    
    if len(df) > limit:
        print(f"\n... and {len(df) - limit} more rows")
    
    print()


def main():
    """Interactive walkthrough main function."""
    
    print_section(
        "Visier Python SDK - Interactive Walkthrough",
        "This walkthrough will teach you how to use the Visier Python SDK\n"
        "to query employee data step by step."
    )
    
    # Check environment variables
    required_vars = [
        "VISIER_HOST",
        "VISIER_APIKEY",
        "VISIER_VANITY",
        "VISIER_USERNAME",
        "VISIER_PASSWORD"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print("❌ Error: Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these in your .env file or environment.")
        print("See visier.env.example for a template.")
        return
    
    print("✅ All required environment variables are set!")
    wait_for_user()
    
    try:
        # STEP 1: Configuration
        print_step(
            1,
            "Configuration Setup",
            "First, we need to configure the SDK with your credentials.\n"
            "The SDK can read configuration from environment variables automatically."
        )
        
        print_code_explanation(
            "config = Configuration.from_env()",
            "This reads all Visier configuration from environment variables:\n"
            "  - VISIER_HOST: Your Visier API endpoint\n"
            "  - VISIER_APIKEY: Your API key\n"
            "  - VISIER_VANITY: Your tenant vanity name\n"
            "  - VISIER_USERNAME & VISIER_PASSWORD: For basic authentication"
        )
        
        print("\n🔧 Creating configuration...")
        sdk_config = get_sdk_config()
        Configuration.set_default(sdk_config)
        print("✅ Configuration created successfully!")
        print(f"   Host: {sdk_config.host}")
        print(f"   Vanity: {sdk_config.vanity}")
        
        wait_for_user()
        
        # STEP 2: API Client
        print_step(
            2,
            "Creating API Client",
            "The ApiClient is your connection to the Visier API.\n"
            "It handles authentication, request formatting, and response parsing automatically."
        )
        
        print_code_explanation(
            "api_client = ApiClient(config)",
            "Creates an API client that will:\n"
            "  - Automatically authenticate when you make your first API call\n"
            "  - Manage authentication tokens for you\n"
            "  - Format requests according to Visier API specifications\n"
            "  - Parse responses into Python objects"
        )
        
        print("\n🔧 Creating API client...")
        api_client = ApiClient(sdk_config)
        print("✅ API client created!")
        print("   (Authentication will happen automatically on first API call)")
        
        wait_for_user()
        
        # STEP 3: Query API
        print_step(
            3,
            "Setting Up Data Query API",
            "The DataQueryApi provides methods to query data from Visier.\n"
            "We'll use it to execute a list query for employee data."
        )
        
        print_code_explanation(
            "data_query_api = DataQueryApi(api_client)",
            "Creates a DataQueryApi instance that provides methods like:\n"
            "  - list(): Execute a list query (returns detailed records)\n"
            "  - aggregate(): Execute an aggregation query (returns summaries)\n"
            "  - snapshot(): Execute a snapshot query (time series data)"
        )
        
        print("\n🔧 Creating DataQueryApi...")
        data_query_api = DataQueryApi(api_client)
        print("✅ DataQueryApi ready!")
        
        wait_for_user()
        
        # STEP 4: Building the Query
        print_step(
            4,
            "Building the Query",
            "A query defines what data you want to retrieve.\n"
            "It specifies the source (analytic object), columns (properties),\n"
            "time period, and other options."
        )
        
        print("\n📋 Query Components:")
        print("   1. Source: Which analytic object to query (e.g., 'Employee')")
        print("   2. Columns: Which properties to retrieve")
        print("   3. Time Interval: What time period to query")
        print("   4. Options: Pagination, limits, etc.")
        
        print_code_explanation(
            """query_dict = {
    "source": {"analyticObject": "Employee"},
    "columns": [
        {"columnName": "Employee ID", 
         "columnDefinition": {
             "property": {
                 "name": "Employee.EmployeeID",
                 "qualifyingPath": "Employee"
             }
         }}
    ],
    "timeInterval": {"fromInstant": "1735689600000"},
    "options": {"limit": 10000, "page": 0}
}""",
            "This query structure tells Visier:\n"
            "  - Query the 'Employee' analytic object\n"
            "  - Return EmployeeID, Time_in_Role, and Span_Of_Control\n"
            "  - Get data from December 1, 2024 onwards\n"
            "  - Return up to 10,000 records"
        )
        
        print("\n🔧 Building query...")
        query_dto = build_query_dto()
        print("✅ Query built successfully!")
        print("   - Analytic Object: Employee")
        print("   - Properties: EmployeeID, Time_in_Role, Span_Of_Control")
        print("   - Time Period: From December 1, 2024")
        
        wait_for_user()
        
        # STEP 5: Executing the Query
        print_step(
            5,
            "Executing the Query",
            "Now we'll send the query to Visier and retrieve the data.\n"
            "The SDK handles all the HTTP communication for us."
        )
        
        print_code_explanation(
            "response = data_query_api.list(query_dto)",
            "This method:\n"
            "  - Sends the query to Visier API\n"
            "  - Handles authentication automatically\n"
            "  - Waits for the response\n"
            "  - Returns a ListResponse object with the data"
        )
        
        print("\n🔧 Executing query...")
        print("   (This may take a few seconds...)")
        response = data_query_api.list(query_dto)
        print("✅ Query executed successfully!")
        print(f"   Response type: {type(response).__name__}")
        
        if hasattr(response, 'rows') and response.rows:
            print(f"   Records returned: {len(response.rows)}")
        
        wait_for_user()
        
        # STEP 6: Processing Results
        print_step(
            6,
            "Processing Results",
            "The response comes back in a structured format.\n"
            "We need to convert it to a more usable format (DataFrame) for analysis."
        )
        
        print_code_explanation(
            """# Response structure:
{
    "header": {"0": "Employee ID", "1": "Time in Role", ...},
    "rows": [
        {"0": "Employee-123", "1": 22, "2": 0},
        ...
    ]
}

# We convert this to a DataFrame with proper column names""",
            "The SDK returns data with numeric keys.\n"
            "We map these to column names and convert to a pandas DataFrame\n"
            "for easier manipulation and analysis."
        )
        
        print("\n🔧 Processing response...")
        df = convert_response_to_dataframe(response)
        print("✅ Data processed successfully!")
        print(f"   Shape: {df.shape[0]} rows, {df.shape[1]} columns")
        
        wait_for_user()
        
        # STEP 7: Display Results
        print_step(
            7,
            "Displaying Results",
            "Finally, let's see the data we retrieved!"
        )
        
        display_results(df, limit=10)
        
        # Summary
        print_section(
            "Walkthrough Complete! 🎉",
            f"Successfully retrieved {len(df)} employee records with:\n"
            f"  - Employee ID\n"
            f"  - Time in Role (months)\n"
            f"  - Span of Control (direct reports)\n\n"
            "Key Takeaways:\n"
            "  1. Configuration: Use Configuration.from_env() for easy setup\n"
            "  2. API Client: Handles authentication automatically\n"
            "  3. Query Structure: Define source, columns, time period, and options\n"
            "  4. Execution: Use DataQueryApi.list() to execute queries\n"
            "  5. Processing: Convert responses to DataFrames for analysis\n\n"
            "Next Steps:\n"
            "  - Try modifying the query to get different properties\n"
            "  - Experiment with different time periods\n"
            "  - Explore other API methods (aggregate, snapshot)\n"
            "  - Check the official SDK documentation for more examples"
        )
        
    except ApiValueError as e:
        print(f"\n❌ Configuration error: {e}")
        print("\nPlease ensure your .env file contains all required variables.")
        return
    except UnauthorizedException as e:
        print(f"\n❌ Authentication failed: {e}")
        print("\nPlease verify your credentials in the .env file")
        return
    except BadRequestException as e:
        print(f"\n❌ Bad request: {e}")
        if hasattr(e, 'body'):
            print(f"  Details: {e.body}")
        return
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        return
    except ServiceException as e:
        print(f"\n❌ Server error: {e.status} - {e.reason}")
        return
    except ApiException as e:
        print(f"\n❌ API Error: {e.status} - {e.reason}")
        return
    except ImportError as e:
        print(f"❌ Error: {e}")
        print("\nPlease install required packages:")
        print("  pip install visier-platform-sdk pandas")
        return
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return


if __name__ == "__main__":
    main()
