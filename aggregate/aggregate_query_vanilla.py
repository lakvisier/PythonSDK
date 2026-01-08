"""
Vanilla HTTP Aggregate Query Implementation

Simple, easy-to-use aggregate query interface for Visier API.
Follows Postman collection pattern - no SDK dependencies.

Quick Start:
    from aggregate_query_vanilla import query_metric
    
    # Simple query - last 6 months
    df = query_metric("employeeCount", dimensions=["Function"])
    
    # With time period
    df = query_metric("employeeCount", dimensions=["Function"], months=6)
    
    # Save to CSV
    df = query_metric("employeeCount", dimensions=["Function"], save_csv="results.csv")

Batch Queries (50+ metrics):
    from aggregate_query_vanilla import query_multiple_metrics, create_selection_concept_filter
    
    # Query 50 metrics with same dimensions and filters
    metrics = ["employeeCount", "turnoverRate", ...]  # 50 metrics
    df = query_multiple_metrics(
        metric_ids=metrics,
        dimensions=["Function", "Gender"],
        dimension_member_filters={"Function": ["Engineering", "Sales"]},
        global_filters=[create_selection_concept_filter("isActive")],
        save_csv="all_metrics.csv"
    )

Advanced Usage:
    from aggregate_query_vanilla import execute_vanilla_aggregate_query
    
    result = execute_vanilla_aggregate_query(
        metric_id="employeeCount",
        axes=[{
            "dimensionLevelSelection": {
                "dimension": {"name": "Function", "qualifyingPath": "Employee"},
                "levelIds": ["Function"]
            }
        }],
        time_intervals={
            "dynamicDateFrom": "SOURCE",
            "intervalPeriodType": "MONTH",
            "intervalCount": 6,
            "direction": "BACKWARD"
        }
    )

References:
    - Postman Collection: https://www.postman.com/visier-alpine/visier-alpine-platform/overview
    - API Reference: See AGGREGATE_QUERY_API_REFERENCE.md
"""

import os
import json
import requests
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_api_config() -> Dict[str, str]:
    """
    Get API configuration from environment variables.
    
    Returns:
        Dictionary with host, apikey, vanity, username, password
    """
    required_vars = [
        "VISIER_HOST",
        "VISIER_APIKEY",
        "VISIER_VANITY",
        "VISIER_USERNAME",
        "VISIER_PASSWORD"
    ]
    
    config = {}
    missing = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing.append(var)
        else:
            config[var.lower().replace("visier_", "")] = value
    
    if missing:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}\n"
            f"Please set these in your .env file. See visier.env.example for a template."
        )
    
    return config


def create_dimension_axis(dimension_name: str, qualifying_path: str = "Employee") -> Dict[str, Any]:
    """
    Helper function to create a dimension axis easily.
    
    Args:
        dimension_name: Name of the dimension (e.g., "Function", "Gender")
        qualifying_path: Qualifying path (default: "Employee")
    
    Returns:
        Axis dictionary ready to use in query
    
    Example:
        axis = create_dimension_axis("Function")
        # Use in query_metric: dimensions=["Function"]
    """
    return {
        "dimensionLevelSelection": {
            "dimension": {
                "name": dimension_name,
                "qualifyingPath": qualifying_path
            },
            "levelIds": [dimension_name]
        }
    }


def create_member_set_filter(
    dimension_name: str,
    included_members: Optional[List[str]] = None,
    excluded_members: Optional[List[str]] = None,
    qualifying_path: str = "Employee"
) -> Dict[str, Any]:
    """
    Create a member set filter to filter by specific dimension members.
    
    This allows you to focus on specific members of a dimension (e.g., only certain Functions).
    
    Args:
        dimension_name: Name of the dimension (e.g., "Function")
        included_members: List of member names to include (e.g., ["Engineering", "Sales"])
                          If None, includes all members
        excluded_members: List of member names to exclude
                          If None, excludes nothing
        qualifying_path: Qualifying path (default: "Employee")
    
    Returns:
        Filter dictionary ready to use in query
    
    Example:
        # Only include Engineering and Sales functions
        filter = create_member_set_filter("Function", included_members=["Engineering", "Sales"])
        
        # Exclude specific functions
        filter = create_member_set_filter("Function", excluded_members=["HR"])
    """
    filter_dict = {
        "memberSet": {
            "dimension": {
                "name": dimension_name,
                "qualifyingPath": qualifying_path
            },
            "values": {}
        }
    }
    
    if included_members:
        filter_dict["memberSet"]["values"]["included"] = [
            {"path": [member]} for member in included_members
        ]
    
    if excluded_members:
        filter_dict["memberSet"]["values"]["excluded"] = [
            {"path": [member]} for member in excluded_members
        ]
    
    return filter_dict


def create_selection_concept_filter(concept_name: str, qualifying_path: str = "Employee") -> Dict[str, Any]:
    """
    Create a selection concept filter (e.g., isManager, isActive).
    
    Args:
        concept_name: Name of the selection concept (e.g., "isManager")
        qualifying_path: Qualifying path (default: "Employee")
    
    Returns:
        Filter dictionary ready to use in query
    
    Example:
        # Filter to only managers
        filter = create_selection_concept_filter("isManager")
    """
    return {
        "selectionConcept": {
            "name": concept_name,
            "qualifyingPath": qualifying_path
        }
    }


def build_vanilla_aggregate_query(
    metric_id: str,
    axes: Optional[List[Dict[str, Any]]] = None,
    filters: Optional[List[Dict[str, Any]]] = None,
    time_intervals: Optional[Dict[str, Any]] = None,
    parameter_values: Optional[List[Dict[str, Any]]] = None,
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Build an aggregate query payload matching the API reference exactly.
    
    Args:
        metric_id: The metric ID to query (e.g., "employeeCount")
        axes: List of axis definitions for grouping. **REQUIRED for aggregate queries.**
              Format: [{"dimensionLevelSelection": {"dimension": {"name": "Gender", "qualifyingPath": "Employee"}, "levelIds": ["Gender"]}}]
        filters: Optional list of filter definitions.
                 Format: [{"selectionConcept": {"name": "isManager", "qualifyingPath": "Employee"}}]
        time_intervals: Optional time interval specification.
                        Both "intervalCount" and "intervalPeriodCount" are valid.
                        Simple: {"intervalCount": 3, "dynamicDateFrom": "SOURCE"}
                        Explicit: {"fromDateTime": "2021-01-01", "intervalPeriodType": "MONTH", "intervalCount": 6}
        parameter_values: Optional parameter values for parameterized metrics.
        options: Optional query options.
                 Common: {"zeroVisibility": "ELIMINATE", "nullVisibility": "ELIMINATE"}
    
    Returns:
        Complete query payload matching API reference schema
    
    Raises:
        ValueError: If axes are not provided (required for aggregate queries)
    """
    if not axes:
        raise ValueError(
            "Aggregate queries require at least one axis (dimension). "
            "Please provide axes parameter with at least one dimension."
        )
    
    query = {
        "source": {
            "metric": metric_id
        },
        "axes": axes
    }
    
    # Add optional components
    if filters:
        query["filters"] = filters
    
    if time_intervals:
        query["timeIntervals"] = time_intervals
    
    if parameter_values:
        query["parameterValues"] = parameter_values
    
    payload = {
        "query": query
    }
    
    if options:
        payload["options"] = options
    
    return payload




def get_asid_token(config: Optional[Dict[str, str]] = None) -> str:
    """
    Get an ASID authentication token using username/password.
    
    Based on Postman collection pattern:
    - Endpoint: POST /v1/admin/visierSecureToken
    - Headers: Content-Type: application/x-www-form-urlencoded
    - Body: form data with username and password
    - Response: ASID token (may be JSON with 'asid' field or plain string)
    
    Args:
        config: Optional API config dict. If None, loads from environment.
    
    Returns:
        ASID token string
    
    Raises:
        ValueError: If required parameters are missing
        requests.HTTPError: If authentication fails
    """
    if config is None:
        config = get_api_config()
    
    # Build the authentication URL (Postman collection pattern)
    host = config["host"].rstrip('/')
    vanity = config["vanity"]
    url = f"{host}/v1/admin/visierSecureToken"
    
    # Prepare headers (Postman collection pattern)
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    
    # Add API key if provided (some endpoints require it)
    if config.get("apikey"):
        headers["apikey"] = config["apikey"]
    
    # Prepare form data (Postman collection pattern)
    form_data = {
        "username": config["username"],
        "password": config["password"]
    }
    
    # Add vanity as query parameter or form data (check Postman collection)
    params = {}
    if vanity:
        params["vanity"] = vanity
    
    # Make the token request
    response = requests.post(
        url,
        headers=headers,
        data=form_data,  # Form-encoded data
        params=params
    )
    
    # Check for errors
    response.raise_for_status()
    
    # Parse token from response
    # Postman collection shows response may be JSON with 'asid' field or plain string
    try:
        # Try parsing as JSON first
        json_response = response.json()
        if isinstance(json_response, dict) and "asid" in json_response:
            token = json_response["asid"]
        elif isinstance(json_response, str):
            token = json_response
        else:
            # If it's a dict but no 'asid' field, try to get the token value
            token = str(json_response)
    except (ValueError, json.JSONDecodeError):
        # Not JSON, treat as plain string
        token = response.text.strip()
    
    # Clean up token (remove quotes if present)
    token = str(token).strip().strip('"').strip("'")
    return token


def execute_vanilla_aggregate_query(
    metric_id: str,
    axes: Optional[List[Dict[str, Any]]] = None,
    filters: Optional[List[Dict[str, Any]]] = None,
    time_intervals: Optional[Dict[str, Any]] = None,
    parameter_values: Optional[List[Dict[str, Any]]] = None,
    options: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, str]] = None,
    asid_token: Optional[str] = None
) -> Dict[str, Any]:
    """
    Execute an aggregate query using vanilla HTTP requests.
    
    Flow: ASID Token (from username/password) + API Key -> Aggregate Query
    
    This bypasses the SDK entirely and makes direct HTTP calls to the Visier API,
    giving us full control over the request payload.
    
    Args:
        metric_id: The metric ID to query
        axes: List of axis definitions (required)
        filters: Optional list of filter definitions
        time_intervals: Optional time interval specification
        parameter_values: Optional parameter values
        options: Optional query options
        config: Optional API config dict. If None, loads from environment.
        asid_token: Optional ASID token. If None, will fetch one automatically using username/password.
    
    Returns:
        Response JSON as dictionary (CellSetDTO structure)
    
    Raises:
        ValueError: If required parameters are missing
        requests.HTTPError: If API request fails
    """
    if config is None:
        config = get_api_config()
    
    # Get ASID token if not provided (uses username/password from config)
    if asid_token is None:
        asid_token = get_asid_token(config)
    
    # Build the query payload
    payload = build_vanilla_aggregate_query(
        metric_id=metric_id,
        axes=axes,
        filters=filters,
        time_intervals=time_intervals,
        parameter_values=parameter_values,
        options=options
    )
    
    # Build the API URL (Postman collection pattern)
    # Try both endpoints - Postman may use /v1/aggregate or /v1/data/query/aggregate
    host = config["host"].rstrip('/')
    vanity = config["vanity"]
    
    # Primary endpoint from API reference
    url = f"{host}/v1/data/query/aggregate"
    
    # Prepare headers (Postman collection pattern)
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Add API key if provided
    if config.get("apikey"):
        headers["apikey"] = config["apikey"]
    
    # Prepare cookies: ASID token as cookie (Postman collection pattern)
    # Postman shows: Cookie: VisierASIDToken=<your_asid_token>
    # So the cookie value is just the token, not "VisierASIDToken={token}"
    cookies = {
        "VisierASIDToken": asid_token
    }
    
    # Prepare query parameters
    params = {}
    if vanity:
        params["vanity"] = vanity
    
    # Make the request
    response = requests.post(
        url,
        json=payload,  # requests will automatically JSON-encode this
        headers=headers,
        cookies=cookies,  # ASID token as cookie (Postman pattern)
        params=params
    )
    
    # Check for errors
    response.raise_for_status()
    
    # Parse and return response
    return response.json()


def convert_vanilla_response_to_dataframe(response: Dict[str, Any]) -> 'pd.DataFrame':
    """
    Convert vanilla API response (CellSetDTO) to pandas DataFrame.
    
    Args:
        response: The API response dictionary (CellSetDTO structure)
    
    Returns:
        pandas DataFrame with dimension columns and metric value column
    """
    import pandas as pd
    
    # Check if response has error
    if "error" in response:
        error = response["error"]
        error_msg = f"Query failed: {error.get('message', 'Unknown error')}"
        if "errorCode" in error:
            error_msg += f" (Code: {error['errorCode']})"
        raise ValueError(error_msg)
    
    # Extract cells and axes (Postman collection response structure)
    # Response is {'cells': [...], 'axes': [...]} at top level (not wrapped in 'cellSet')
    cells = response.get("cells", [])
    axes = response.get("axes", [])
    
    if not cells:
        return pd.DataFrame()
    
    if not axes:
        # No axes - just return metric values
        values = []
        for cell in cells:
            cell_value = cell.get("value")
            if cell_value is None or cell_value == "":
                values.append(None)
            else:
                try:
                    values.append(float(cell_value))
                except (ValueError, TypeError):
                    values.append(None)
        return pd.DataFrame({"value": values})
    
    # Build dimension names from axes
    dimension_names = []
    for axis in axes:
        if "dimension" in axis and axis["dimension"]:
            dim_name = axis["dimension"].get("name", f"Dimension_{len(dimension_names)}")
            dimension_names.append(dim_name)
        else:
            dimension_names.append(f"Dimension_{len(dimension_names)}")
    
    # Build position lookup for each axis
    # Positions have 'path' arrays - use the last element or full path
    axis_positions = []
    for axis in axes:
        positions = {}
        if "positions" in axis:
            for i, position in enumerate(axis["positions"]):
                if "path" in position:
                    path = position["path"]
                    if isinstance(path, list) and len(path) > 0:
                        # Use the last element of the path (most specific)
                        position_name = str(path[-1])
                    else:
                        position_name = str(path)
                elif "members" in position and position["members"]:
                    # Fallback: try members if path not available
                    member = position["members"][0]
                    position_name = member.get("name") or member.get("memberId") or f"Position_{i}"
                else:
                    position_name = f"Position_{i}"
                positions[i] = position_name
        axis_positions.append(positions)
    
    # Build DataFrame rows
    rows = []
    for cell in cells:
        row = {}
        
        # Add dimension values from cell coordinates
        # Coordinates are indices into the axes positions
        if "coordinates" in cell:
            coordinates = cell["coordinates"]
            for i, coord_idx in enumerate(coordinates):
                if i < len(axis_positions):
                    dim_name = dimension_names[i] if i < len(dimension_names) else f"Dimension_{i}"
                    pos_map = axis_positions[i]
                    row[dim_name] = pos_map.get(coord_idx, f"Position_{coord_idx}")
        
        # Add metric value (handle empty strings and None)
        cell_value = cell.get("value")
        if cell_value is None or cell_value == "":
            row["value"] = None
        else:
            try:
                row["value"] = float(cell_value)
            except (ValueError, TypeError):
                row["value"] = None
        
        # Add support if available
        if "support" in cell:
            support_value = cell.get("support")
            if support_value is None or support_value == "":
                row["support"] = None
            else:
                try:
                    row["support"] = int(support_value)
                except (ValueError, TypeError):
                    row["support"] = None
        
        rows.append(row)
    
    return pd.DataFrame(rows)


def query_metric(
    metric_id: str,
    dimensions: Optional[List[str]] = None,
    qualifying_path: str = "Employee",
    months: int = 6,
    direction: str = "BACKWARD",
    save_csv: Optional[str] = None,
    filters: Optional[List[Dict[str, Any]]] = None,
    options: Optional[Dict[str, Any]] = None
) -> 'pd.DataFrame':
    """
    Simple function to query a metric and get results as a DataFrame.
    
    This is the easiest way to use aggregate queries - just provide the metric
    and dimensions, and get back a pandas DataFrame.
    
    Args:
        metric_id: The metric to query (e.g., "employeeCount")
        dimensions: List of dimension names (e.g., ["Function", "Gender"])
                   If None, uses just the metric (no grouping)
        qualifying_path: Qualifying path for dimensions (default: "Employee")
        months: Number of months to query (default: 6)
        direction: "BACKWARD" (last N months) or "FORWARD" (next N months)
        save_csv: Optional filename to save results as CSV
        filters: Optional list of filter definitions
        options: Optional query options
    
    Returns:
        pandas DataFrame with results
    
    Example:
        # Simple query - last 6 months by Function
        df = query_metric("employeeCount", dimensions=["Function"])
        
        # Multiple dimensions
        df = query_metric("employeeCount", dimensions=["Function", "Gender"])
        
        # Save to CSV
        df = query_metric("employeeCount", dimensions=["Function"], save_csv="results.csv")
        
        # Different time period
        df = query_metric("employeeCount", dimensions=["Function"], months=12)
    """
    import pandas as pd
    
    # Build axes from dimension names
    axes = None
    if dimensions:
        axes = [create_dimension_axis(dim, qualifying_path) for dim in dimensions]
    else:
        # At least one axis is required - use a simple time axis or default
        # Actually, let's require at least one dimension for simplicity
        raise ValueError(
            "At least one dimension is required. "
            "Example: query_metric('employeeCount', dimensions=['Function'])"
        )
    
    # Build time intervals (last N months by default)
    time_intervals = {
        "dynamicDateFrom": "SOURCE",
        "intervalPeriodType": "MONTH",
        "intervalCount": months,
        "direction": direction
    }
    
    # Execute query
    response = execute_vanilla_aggregate_query(
        metric_id=metric_id,
        axes=axes,
        filters=filters,
        time_intervals=time_intervals,
        options=options
    )
    
    # Convert to DataFrame
    df = convert_vanilla_response_to_dataframe(response)
    
    # Save to CSV if requested
    if save_csv:
        df.to_csv(save_csv, index=False)
        print(f"✓ Results saved to: {save_csv}")
    
    return df


def query_multiple_metrics(
    metric_ids: List[str],
    dimensions: List[str],
    qualifying_path: str = "Employee",
    months: int = 6,
    direction: str = "BACKWARD",
    dimension_member_filters: Optional[Dict[str, List[str]]] = None,
    global_filters: Optional[List[Dict[str, Any]]] = None,
    options: Optional[Dict[str, Any]] = None,
    save_csv: Optional[str] = None,
    progress: bool = True
) -> 'pd.DataFrame':
    """
    Query multiple metrics with the same dimensions and filters.
    
    This is optimized for batch queries where you want to pull many metrics
    (e.g., 50 metrics) with the same structure:
    - Same dimensions (2-3 dimensions)
    - Same dimension member filters (focus on specific members)
    - Same global filters (apply to all metrics)
    
    Args:
        metric_ids: List of metric IDs to query (e.g., ["employeeCount", "turnoverRate"])
        dimensions: List of dimension names for grouping (e.g., ["Function", "Gender"])
        qualifying_path: Qualifying path for dimensions (default: "Employee")
        months: Number of months to query (default: 6)
        direction: "BACKWARD" (last N months) or "FORWARD" (next N months)
        dimension_member_filters: Dict mapping dimension names to lists of members to include.
                                  Example: {"Function": ["Engineering", "Sales"], "Gender": ["Male"]}
                                  If None, includes all members for all dimensions.
        global_filters: List of filter definitions that apply to all metrics.
                        Can include selection concepts, member sets, etc.
                        Example: [create_selection_concept_filter("isManager")]
        options: Optional query options
        save_csv: Optional filename to save combined results as CSV
        progress: Whether to show progress (default: True)
    
    Returns:
        pandas DataFrame with all metrics combined. Each row has:
        - Dimension columns (Function, Gender, etc.)
        - Metric columns (one per metric_id)
        - Time period columns (DateInRange, etc.)
    
    Example:
        # Query 50 metrics by Function and Gender, only for Engineering and Sales
        metrics = ["employeeCount", "turnoverRate", "headcount", ...]  # 50 metrics
        df = query_multiple_metrics(
            metric_ids=metrics,
            dimensions=["Function", "Gender"],
            dimension_member_filters={"Function": ["Engineering", "Sales"]},
            global_filters=[create_selection_concept_filter("isActive")],
            save_csv="all_metrics.csv"
        )
    """
    import pandas as pd
    
    if not metric_ids:
        raise ValueError("At least one metric_id is required")
    
    if not dimensions:
        raise ValueError("At least one dimension is required")
    
    # Build axes
    axes = [create_dimension_axis(dim, qualifying_path) for dim in dimensions]
    
    # Build dimension member filters
    all_filters = []
    if dimension_member_filters:
        for dim_name, members in dimension_member_filters.items():
            filter_dict = create_member_set_filter(
                dim_name,
                included_members=members,
                qualifying_path=qualifying_path
            )
            all_filters.append(filter_dict)
    
    # Add global filters
    if global_filters:
        all_filters.extend(global_filters)
    
    # Build time intervals
    time_intervals = {
        "dynamicDateFrom": "SOURCE",
        "intervalPeriodType": "MONTH",
        "intervalCount": months,
        "direction": direction
    }
    
    # Query each metric and combine results
    all_dfs = []
    total_metrics = len(metric_ids)
    
    for i, metric_id in enumerate(metric_ids):
        if progress:
            print(f"Querying {metric_id} ({i+1}/{total_metrics})...", end=" ", flush=True)
        
        try:
            response = execute_vanilla_aggregate_query(
                metric_id=metric_id,
                axes=axes,
                filters=all_filters if all_filters else None,
                time_intervals=time_intervals,
                options=options
            )
            
            df = convert_vanilla_response_to_dataframe(response)
            
            # Rename 'value' column to metric_id to distinguish metrics
            if "value" in df.columns:
                df = df.rename(columns={"value": metric_id})
            
            all_dfs.append(df)
            
            if progress:
                print(f"✓ ({len(df)} rows)")
        
        except Exception as e:
            if progress:
                print(f"✗ Error: {e}")
            # Continue with other metrics even if one fails
            continue
    
    if not all_dfs:
        raise ValueError("No metrics were successfully queried")
    
    # Merge all DataFrames on dimension columns
    # Find common dimension columns (exclude metric columns, Measures, DateInRange, support)
    dimension_cols = set()
    for df in all_dfs:
        for col in df.columns:
            if col not in ["Measures", "DateInRange", "support"] and col not in metric_ids:
                dimension_cols.add(col)
    
    dimension_cols = sorted(list(dimension_cols))
    
    # Start with first DataFrame
    combined_df = all_dfs[0].copy()
    
    # Merge remaining DataFrames
    for df in all_dfs[1:]:
        # Merge on dimension columns and time columns
        merge_cols = dimension_cols.copy()
        if "DateInRange" in combined_df.columns and "DateInRange" in df.columns:
            merge_cols.append("DateInRange")
        
        # Only merge if we have merge columns
        if merge_cols:
            combined_df = pd.merge(
                combined_df,
                df,
                on=merge_cols,
                how="outer",
                suffixes=("", "_dup")
            )
            
            # Remove duplicate columns (keep first occurrence)
            for col in combined_df.columns:
                if col.endswith("_dup"):
                    combined_df = combined_df.drop(columns=[col])
        else:
            # If no merge columns, just concatenate (shouldn't happen with proper dimensions)
            combined_df = pd.concat([combined_df, df], axis=1)
    
    # Reorder columns: dimensions first, then metrics, then other columns
    metric_cols = [m for m in metric_ids if m in combined_df.columns]
    other_cols = [c for c in combined_df.columns if c not in dimension_cols and c not in metric_cols]
    column_order = dimension_cols + metric_cols + other_cols
    combined_df = combined_df[[c for c in column_order if c in combined_df.columns]]
    
    # Save to CSV if requested
    if save_csv:
        combined_df.to_csv(save_csv, index=False)
        if progress:
            print(f"\n✓ Combined results saved to: {save_csv}")
    
    return combined_df


def display_vanilla_results(df: 'pd.DataFrame', metric_name: str = "Metric"):
    """
    Display results from vanilla aggregate query.
    
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
    Main function - demonstrates simple usage of query_metric().
    """
    print("=" * 70)
    print("Visier Aggregate Query - Simple Demo")
    print("=" * 70)
    print()
    
    try:
        # Simple usage example
        print("Querying employeeCount by Function and Pay_Level (last 6 months)...")
        print()
        
        import os
        # Save to output directory relative to this script
        output_dir = os.path.join(os.path.dirname(__file__), "output")
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "aggregate_query_results.csv")
        
        df = query_metric(
            metric_id="employeeCount",
            dimensions=["Function", "Pay_Level"],
            months=6,
            save_csv=output_file
        )
        
        print("\n" + "=" * 70)
        print("Query Results Summary")
        print("=" * 70)
        print(f"  Rows: {len(df)}")
        print(f"  Columns: {', '.join(df.columns)}")
        if "value" in df.columns:
            non_null = df["value"].notna().sum()
            print(f"  Rows with values: {non_null} / {len(df)}")
            if non_null > 0:
                print(f"  Value range: {df['value'].min():.2f} - {df['value'].max():.2f}")
                print(f"  Total: {df['value'].sum():.2f}")
        print("=" * 70)
        print()
        print("💡 Tip: Use query_metric() in your code:")
        print("   from aggregate_query_vanilla import query_metric")
        print("   df = query_metric('employeeCount', dimensions=['Function'])")
        print()
        
    except ValueError as e:
        print(f"\n✗ Error: {e}")
        print("\nMake sure you have:")
        print("  - Set up .env file with your Visier credentials")
        print("  - Provided at least one dimension")
        return
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return


if __name__ == "__main__":
    main()
