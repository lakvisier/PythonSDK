"""
Aggregate Query Demo for Visier Platform.

This script demonstrates how to execute aggregate queries for predefined metrics
using the Visier Python SDK. Aggregate queries return aggregated summaries
(grouped by dimensions) rather than detailed records.

This script demonstrates:
- Building aggregate queries with metrics, axes (dimensions), filters, and time intervals
- Executing aggregate queries using DataQueryApi.aggregate()
- Handling CellSetOrErrorDTO response structure
- Converting CellSetDTO to pandas DataFrame

Usage:
    python aggregate_query.py

Environment variables (see visier.env.example):
    VISIER_HOST, VISIER_APIKEY, VISIER_VANITY (required)
    VISIER_USERNAME, VISIER_PASSWORD (required for Basic Auth)
"""

import sys
import warnings
from datetime import datetime
from typing import Optional, List, Dict, Any

warnings.filterwarnings('ignore', message='.*urllib3.*NotOpenSSLWarning.*')
warnings.filterwarnings('ignore', message='.*urllib3 v2 only supports OpenSSL.*')

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from visier_platform_sdk import ApiClient, Configuration, DataQueryApi
from visier_platform_sdk.models import (
    AggregationQueryExecutionDTO,
    CellSetOrErrorDTO,
    CellSetDTO,
    CellDTO,
    CellSetAxisDTO
)
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
    """
    Get SDK Configuration from environment variables.
    Uses Configuration.from_env() as recommended in the official SDK documentation.
    """
    return Configuration.from_env()


def build_aggregate_query_dto(
    metric_id: str,
    axes: Optional[List[Dict[str, Any]]] = None,
    filters: Optional[List[Dict[str, Any]]] = None,
    time_intervals: Optional[Dict[str, Any]] = None,
    options: Optional[Dict[str, Any]] = None
) -> tuple[AggregationQueryExecutionDTO, Dict[str, Any]]:
    """
    Build an AggregationQueryExecutionDTO from parameters.
    
    Args:
        metric_id: The metric ID to query (e.g., "employeeCount")
        axes: List of axis definitions for grouping. **REQUIRED for aggregate queries.**
              Format: [{"dimensionLevelSelection": {"dimension": {"name": "Gender", "qualifyingPath": "Employee"}, "levelIds": ["Gender"]}}]
              Note: Use "name" and "qualifyingPath" in the input - the workaround will preserve them.
        filters: Optional list of filter definitions.
                 Format: [{"selectionConcept": {"name": "isManager", "qualifyingPath": "Employee"}}]
        time_intervals: Optional time interval specification.
                        Both "intervalCount" and "intervalPeriodCount" are valid (API accepts both).
                        Simple: {"intervalCount": 3, "dynamicDateFrom": "SOURCE"}
                        Explicit: {"fromDateTime": "2021-01-01", "intervalPeriodType": "MONTH", "intervalCount": 6}
                        With direction: {"fromDateTime": "2021-01-01", "intervalPeriodType": "MONTH", "intervalCount": 6, "direction": "BACKWARD"}
                        See API reference for full schema including shift, trailingPeriod, etc.
        options: Optional query options. Common options:
                 - zeroVisibility: "SHOW" | "HIDE" | "ELIMINATE" (default: "SHOW")
                 - nullVisibility: "SHOW" | "HIDE" | "ELIMINATE" (default: "SHOW")
                 - enableSparseResults: bool (only return non-zero/non-null cells)
                 - calendarType: "TENANT_CALENDAR" | "GREGORIAN_CALENDAR"
                 - memberDisplayMode: "DEFAULT" | "COMPACT" | "DISPLAY" | "MDX" | "COMPACT_DISPLAY"
                 - axesOverallValueMode: "NONE" | "AGGREGATE" | "OVERALL"
                 See API reference for full options schema
    
    Returns:
        Tuple of (AggregationQueryExecutionDTO, original_query_dict)
        The original_query_dict preserves dimension info that the SDK loses.
    
    Note:
        Aggregate queries typically require at least one axis (dimension) to return data.
        The SDK's DimensionReferenceDTO model loses "name" and "qualifyingPath", so we
        use a workaround to preserve them in the original_query_dict.
    """
    if not axes:
        raise ValueError(
            "Aggregate queries require at least one axis (dimension). "
            "Please provide axes parameter with at least one dimension."
        )
    
    query_dict = {
        "query": {
            "source": {
                "metric": metric_id
            }
        }
    }
    
    # Add axes (required for aggregate queries)
    query_dict["query"]["axes"] = axes
    
    # Add filters if provided
    if filters:
        query_dict["query"]["filters"] = filters
    
    # Add time intervals if provided
    if time_intervals:
        query_dict["query"]["timeIntervals"] = time_intervals
    
    # Add options if provided
    if options:
        query_dict["query"]["options"] = options
    
    # Use from_dict() to create the DTO
    # Note: This may lose dimension info (name/qualifyingPath) due to SDK limitation
    # So we return both the DTO and the original dict
    query_dto = AggregationQueryExecutionDTO.from_dict(query_dict)
    
    return query_dto, query_dict


def execute_aggregate_query(
    query_dto: AggregationQueryExecutionDTO,
    api_client: Optional[ApiClient] = None,
    original_query_dict: Optional[Dict[str, Any]] = None
) -> CellSetDTO:
    """
    Execute an aggregate query and return the CellSetDTO.
    
    Note: Due to a mismatch between the SDK's DimensionReferenceDTO model (which only has objectName)
    and the API's expectations (which require name and qualifyingPath), we use the original query dict
    to preserve the correct format.
    
    Args:
        query_dto: The AggregationQueryExecutionDTO to execute (may have lost dimension info)
        api_client: Optional ApiClient. If None, creates a new one.
        original_query_dict: Optional original query dict with name/qualifyingPath format
    
    Returns:
        CellSetDTO containing cells and axes
    
    Raises:
        ValueError: If the query failed (response contains error)
        ApiException: If API call failed
    """
    if api_client is None:
        sdk_config = get_sdk_config()
        Configuration.set_default(sdk_config)
        api_client = ApiClient(sdk_config)
    
    # Workaround: Use REST client directly to send properly formatted JSON
    # The SDK's DimensionReferenceDTO loses name/qualifyingPath, so we bypass DTO validation
    import json
    from visier_platform_sdk.rest import RESTResponse
    from visier_platform_sdk.models import CellSetOrErrorDTO
    
    # Use original query dict if provided (has correct format), otherwise use DTO
    if original_query_dict:
        query_dict_to_send = original_query_dict
    else:
        query_dict_to_send = query_dto.to_dict()
        # Try to fix dimensions if they're empty
        if "query" in query_dict_to_send and "axes" in query_dict_to_send["query"]:
            for axis in query_dict_to_send["query"]["axes"]:
                if "dimensionLevelSelection" in axis:
                    dim_level = axis["dimensionLevelSelection"]
                    if "dimension" in dim_level:
                        dim = dim_level["dimension"]
                        # If dimension is empty, we can't fix it
                        if not dim or (not dim.get("name") and not dim.get("objectName")):
                            raise ValueError(
                                "Dimension information was lost. Please provide original_query_dict."
                            )
    
    # Use the DataQueryApi but with a workaround: manually construct the request
    # Since the SDK's DTO validation loses dimension info, we'll use from_json with
    # a properly formatted JSON string that preserves the dimension structure
    data_query_api = DataQueryApi(api_client)
    
    # Convert the fixed dict to JSON and use from_json
    # This should preserve the structure better than from_dict
    query_json = json.dumps(query_dict_to_send)
    query_dto_fixed = AggregationQueryExecutionDTO.from_json(query_json)
    
    # However, from_json still loses the dimension. Let's try a different approach:
    # Use the REST client's request method directly
    from visier_platform_sdk.rest import RESTClientObject
    
    # Actually, let's just use the API method but ensure we're passing the right format
    # The issue is that from_dict/from_json both lose the dimension
    # So we need to manually patch the DTO after creation or use a different method
    
    # WORKAROUND: Manually patch the DTO's internal structure to restore dimension info
    # The SDK's DimensionReferenceDTO loses name/qualifyingPath, so we patch it back
    data_query_api = DataQueryApi(api_client)
    
    if original_query_dict and query_dto.query and query_dto.query.axes:
        # Extract original dimension info
        original_axes = original_query_dict.get("query", {}).get("axes", [])
        
        # Patch each axis in the DTO
        for i, axis in enumerate(query_dto.query.axes):
            if i < len(original_axes) and original_axes[i].get("dimensionLevelSelection"):
                orig_dim_level = original_axes[i]["dimensionLevelSelection"]
                orig_dim = orig_dim_level.get("dimension", {})
                
                # If we have original dimension info with name/qualifyingPath
                if orig_dim.get("name") and orig_dim.get("qualifyingPath"):
                    # Patch the dimension object in the DTO
                    if axis.dimension_level_selection and axis.dimension_level_selection.dimension:
                        dim_obj = axis.dimension_level_selection.dimension
                        # Use model's __dict__ to inject the missing fields
                        # Pydantic models allow setting attributes that aren't in the schema
                        # We'll set them directly on the model instance
                        if hasattr(dim_obj, '__dict__'):
                            # Store original values in model's __dict__
                            dim_obj.__dict__['name'] = orig_dim["name"]
                            dim_obj.__dict__['qualifyingPath'] = orig_dim["qualifyingPath"]
                        # Also try setting as attributes (Pydantic v2 might allow this)
                        try:
                            setattr(dim_obj, 'name', orig_dim["name"])
                            setattr(dim_obj, 'qualifyingPath', orig_dim["qualifyingPath"])
                        except:
                            pass
    
    # WORKAROUND: Override the to_dict method temporarily to inject dimension info
    # This is a more reliable approach - we'll create a custom serialization
    if original_query_dict:
        # Create a patched version of the DTO's to_dict output
        dto_dict = query_dto.to_dict()
        
        # Restore dimension info from original_query_dict
        if "query" in dto_dict and "axes" in dto_dict["query"]:
            original_axes = original_query_dict.get("query", {}).get("axes", [])
            for i, axis_dict in enumerate(dto_dict["query"]["axes"]):
                if i < len(original_axes) and "dimensionLevelSelection" in axis_dict:
                    orig_axis = original_axes[i]
                    if "dimensionLevelSelection" in orig_axis:
                        orig_dim = orig_axis["dimensionLevelSelection"].get("dimension", {})
                        if orig_dim.get("name") and orig_dim.get("qualifyingPath"):
                            # Patch the dimension in the serialized dict
                            axis_dict["dimensionLevelSelection"]["dimension"] = {
                                "name": orig_dim["name"],
                                "qualifyingPath": orig_dim["qualifyingPath"]
                            }
        
        # Now we need to send this patched dict to the API
        # Use the SDK's REST client to send the properly formatted JSON
        from visier_platform_sdk.rest import RESTClientObject
        
        # Build the full URL
        config = api_client.configuration
        base_url = config.host.rstrip('/')
        resource_path = "/v1/data/query/aggregate"
        url = f"{base_url}{resource_path}"
        
        # Prepare headers
        header_params = api_client.default_headers.copy()
        header_params['Content-Type'] = 'application/json'
        header_params['Accept'] = 'application/json'
        
        # Serialize the patched dict using SDK's sanitize_for_serialization
        # The REST client will handle JSON encoding, so pass dict directly
        serialized_body = api_client.sanitize_for_serialization(dto_dict)
        
        # Make the API call using call_api
        # Note: REST client's request() method does json.dumps() on the body if it's a dict
        # So we pass the dict directly, not a JSON string
        response_data = api_client.call_api(
            'POST',
            url,
            header_params=header_params,
            body=serialized_body  # Pass dict, not JSON string
        )
        
        # Deserialize the response
        response_data.read()
        response_text = response_data.data.decode('utf-8')
        response_dict = json.loads(response_text)
        
        # Check for HTTP errors
        if response_data.status not in [200, 201]:
            from visier_platform_sdk.exceptions import ApiException
            raise ApiException.from_response(
                http_resp=response_data,
                body=response_text,
                data=response_dict
            )
        
        # Deserialize response using response_deserialize
        api_response = api_client.response_deserialize(
            response_data,
            response_types_map={
                '200': CellSetOrErrorDTO,
                '400': 'dict',
                '500': 'dict'
            }
        )
        
        response: CellSetOrErrorDTO = api_response.data
    else:
        # Fallback: Use standard API method (will likely fail due to missing dimension)
        response: CellSetOrErrorDTO = data_query_api.aggregate(query_dto)
    
    # Check for errors
    if response.error:
        error_msg = f"Query failed: {response.error}"
        if hasattr(response.error, 'message'):
            error_msg += f" - {response.error.message}"
        if hasattr(response.error, 'error_code'):
            error_msg += f" (Code: {response.error.error_code})"
        raise ValueError(error_msg)
    
    # Extract the cell set
    if response.cell_set is None:
        # This might be valid - some queries return empty results
        # Create an empty CellSetDTO structure
        from visier_platform_sdk.models import CellSetDTO
        return CellSetDTO(cells=[], axes=[])
    
    return response.cell_set


def convert_cellset_to_dataframe(cell_set: CellSetDTO) -> pd.DataFrame:
    """
    Convert CellSetDTO to pandas DataFrame.
    
    This creates a flattened DataFrame where each row represents a cell
    with columns for each dimension and the metric value.
    
    Args:
        cell_set: The CellSetDTO to convert
    
    Returns:
        pandas DataFrame with dimension columns and metric value column
    """
    if cell_set is None:
        raise ValueError("CellSet is None")
    
    if not cell_set.cells:
        # Return empty DataFrame with appropriate structure
        return pd.DataFrame()
    
    if not cell_set.axes:
        # No axes - just return metric values
        values = [float(cell.value) if cell.value else None for cell in cell_set.cells]
        return pd.DataFrame({"value": values})
    
    # Build dimension names from axes
    dimension_names = []
    for axis in cell_set.axes:
        if axis.dimension:
            dim_name = axis.dimension.name if hasattr(axis.dimension, 'name') else f"Dimension_{len(dimension_names)}"
            dimension_names.append(dim_name)
        else:
            dimension_names.append(f"Dimension_{len(dimension_names)}")
    
    # Build position lookup for each axis
    axis_positions = []
    for axis in cell_set.axes:
        positions = {}
        if axis.positions:
            for idx, position in enumerate(axis.positions):
                # Extract the display value from position
                # Priority: display_name > last element of path > full path > index
                display_name = None
                
                # Try display_name first (most user-friendly)
                if hasattr(position, 'display_name') and position.display_name:
                    display_name = position.display_name
                # Try display_name_path (alternative display name)
                elif hasattr(position, 'display_name_path') and position.display_name_path:
                    if isinstance(position.display_name_path, list) and len(position.display_name_path) > 0:
                        display_name = position.display_name_path[-1]
                # Fall back to path
                elif hasattr(position, 'path') and position.path:
                    if isinstance(position.path, list) and len(position.path) > 0:
                        # Use the last element of the path (most specific)
                        display_name = str(position.path[-1])
                    else:
                        display_name = str(position.path)
                
                # Final fallback
                if not display_name:
                    display_name = f"Position_{idx}"
                
                positions[idx] = display_name
        axis_positions.append(positions)
    
    # Build rows from cells
    rows = []
    for cell in cell_set.cells:
        if not cell.coordinates:
            # Cell without coordinates - skip or handle specially
            continue
        
        row = {}
        
        # Map coordinates to dimension values
        for axis_idx, coord in enumerate(cell.coordinates):
            if axis_idx < len(axis_positions):
                dim_name = dimension_names[axis_idx]
                position_map = axis_positions[axis_idx]
                row[dim_name] = position_map.get(coord, f"Unknown_{coord}")
            else:
                row[f"Dimension_{axis_idx}"] = f"Coord_{coord}"
        
        # Add metric value
        row["value"] = float(cell.value) if cell.value and cell.value != "" else None
        
        # Add support if available
        if cell.support:
            row["support"] = int(cell.support) if cell.support else None
        
        rows.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(rows)
    
    # Reorder columns: dimensions first, then value, then support
    if not df.empty:
        value_cols = [col for col in ["value", "support"] if col in df.columns]
        dim_cols = [col for col in df.columns if col not in value_cols]
        df = df[dim_cols + value_cols]
    
    return df


def display_results(df: pd.DataFrame, metric_name: str = "Metric"):
    """
    Display query results in a simple table format.
    
    Args:
        df: The DataFrame to display
        metric_name: Name of the metric for display purposes
    """
    if df is None or df.empty:
        print(f"\nNo data returned from {metric_name} query.")
        return
    
    print("\n" + "=" * 70)
    print(f"{metric_name} Query Results")
    print("=" * 70)
    print(f"\nFound {len(df)} result(s):\n")
    
    # Display first 50 rows
    print(df.head(50).to_string(index=False))
    
    if len(df) > 50:
        print(f"\n... and {len(df) - 50} more rows")
    
    print(f"\nSummary:")
    print(f"  Total rows: {len(df)}")
    print(f"  Columns: {', '.join(df.columns)}")
    if "value" in df.columns:
        print(f"  Value range: {df['value'].min():.2f} - {df['value'].max():.2f}")
        print(f"  Total value: {df['value'].sum():.2f}")
    print()


def main():
    """
    Main function to run the aggregate query demo.
    """
    print("=" * 70)
    print("Visier Aggregate Query Demo")
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
        # Step 1: Create client
        print("Step 1: Creating API client...")
        sdk_config = get_sdk_config()
        Configuration.set_default(sdk_config)
        api_client = ApiClient(sdk_config)
        print("✓ API client created")
        print()
        
        # Step 2: Build aggregate query using SDK test file structure (without filter)
        print("Step 2: Building aggregate query...")
        print("  Metric: employeeCount (from SDK test file)")
        print("  Axes: Function, Pay_Level")
        print("  Filters: None (isManager not available in tenant)")
        print("  Time intervals: 2021-01-01, 6 months")
        print("  Using intervalCount (from test file)")
        
        # Use the exact structure from SDK test file aggregate.json (without filter)
        query_dto, original_query_dict = build_aggregate_query_dto(
            metric_id="employeeCount",
            axes=[
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
            filters=None,  # Filter concept not available in tenant
            time_intervals={
                "fromDateTime": "2021-01-01",
                "intervalPeriodType": "MONTH",
                "intervalCount": 6  # Test file uses intervalCount
            }
        )
        print("✓ Query built")
        print()
        
        # Step 3: Execute query
        print("Step 3: Executing aggregate query...")
        try:
            cell_set = execute_aggregate_query(query_dto, api_client, original_query_dict)
            print("✓ Query executed successfully")
            if cell_set.cells:
                print(f"  Cells returned: {len(cell_set.cells)}")
            if cell_set.axes:
                print(f"  Axes (dimensions): {len(cell_set.axes)}")
            print()
        except ValueError as e:
            print(f"\n⚠ Query error: {e}")
            print("\nThis might indicate:")
            print("  - The metric ID 'employeeCount' doesn't exist in your tenant")
            print("  - There's no data available for the specified time period")
            print("  - You don't have permissions to access this data")
            print("\nTry:")
            print("  1. Verify the metric ID in your Visier tenant")
            print("  2. Check available metrics using the Metrics API")
            print("  3. Try a different time period")
            print("  4. Verify your permissions")
            return
        except ServiceException as e:
            print(f"\n⚠ SDK returned server error (500).", file=sys.stderr)
            print(f"Error code: {e.data.get('code', 'Unknown') if hasattr(e, 'data') and e.data else 'Unknown'}", file=sys.stderr)
            raise
        except ApiException as e:
            print(f"\n⚠ API error occurred: {e}", file=sys.stderr)
            if hasattr(e, 'body'):
                print(f"Response body: {e.body}", file=sys.stderr)
            raise
        
        # Step 4: Process and display results
        print("Step 4: Processing results...")
        if not cell_set.cells or len(cell_set.cells) == 0:
            print("⚠ No cells returned in the response.")
            print("This could mean:")
            print("  - The metric doesn't exist in your tenant")
            print("  - There's no data for the specified time period")
            print("  - The metric ID might be different")
            print("\n💡 Tip: Use 'python metric_discovery.py' to find available predefined metrics")
            print("\nResponse structure:")
            print(f"  Axes: {len(cell_set.axes) if cell_set.axes else 0}")
            print(f"  Cells: {len(cell_set.cells) if cell_set.cells else 0}")
            return
        
        df = convert_cellset_to_dataframe(cell_set)
        display_results(df, "Employee Count")
        
        print("=" * 70)
        print("Demo completed successfully!")
        if not df.empty:
            print(f"  Shape: {df.shape[0]} rows, {df.shape[1]} columns")
        print("=" * 70)
        
    except ApiValueError as e:
        print(f"\n✗ Configuration error: {e}")
        print("\nPlease ensure your .env file contains all required variables.")
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
        print("  - Metric ID doesn't exist in your tenant")
        print("  - Dimension doesn't exist or isn't available")
        print("  - Missing required query parameters")
        return
    except ValueError as e:
        print(f"\n✗ Error: {e}")
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
