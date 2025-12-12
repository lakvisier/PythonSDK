# Visier Employee Data Query Demo

A simple Python script to query employee data from the Visier Platform using the official Visier Python SDK.

## Overview

This project demonstrates how to:
- Authenticate with Visier Platform using basic authentication
- Query employee data for a specific time period (recent month)
- Retrieve specific employee properties: EmployeeID, Time_in_Role, and Span_Of_Control
- Display results in a readable format

## Prerequisites

- Python 3.9 or higher
- Visier Platform account with API access
- API credentials (API key, username, password, vanity name)

## Installation

1. **Clone or download this repository**

2. **Create a virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. **Copy the example environment file**:
   ```bash
   cp visier.env.example .env
   ```

2. **Edit `.env` with your Visier credentials**:
   ```env
   VISIER_HOST=https://your-tenant.api.visier.io
   VISIER_APIKEY=your-api-key
   VISIER_VANITY=your-vanity-name
   VISIER_USERNAME=your-username
   VISIER_PASSWORD=your-password
   ```

   **⚠️ Security Note:** Never commit your `.env` file to version control. It's already included in `.gitignore`.

## Usage

### Quick Demo Script

Run the simple demo script:
```bash
python employee_query.py
```

This script quickly queries and displays employee data.

### Interactive Walkthrough (Recommended for Learning)

**Option 1: Python Script**
```bash
python interactive_walkthrough.py
```

**Option 2: Jupyter Notebook (Best for Learning)**
```bash
jupyter notebook visier_sdk_walkthrough.ipynb
```

The interactive walkthrough:
- Explains each step in detail
- Shows code examples with explanations
- Allows you to run code step-by-step
- Teaches SDK concepts as you go
- Perfect for learning how the SDK works
- **Notebook version**: Run cells individually, see results immediately, modify and experiment

The script will:
1. Load credentials from your `.env` file
2. Authenticate with Visier Platform
3. Query employee data for the recent month (from the first day of the current month)
4. Display results showing EmployeeID, Time in Role, and Span of Control

### Example Output

```
======================================================================
Visier Employee Data Query Demo
======================================================================

Step 1: Creating API client...
✓ API client created
  (Authentication will happen automatically on first API call)

Step 2: Building query...
  Time period: From 2025-12-01 (start of current month)
  Analytic Object: Employee
  Properties: EmployeeID, Time_in_Role, Span_Of_Control
✓ Query built

Step 3: Executing query...
✓ Query executed successfully

Step 4: Processing results...

======================================================================
Query Results
======================================================================

Found 4349 employee record(s):

  Employee ID  Time in Role  Span of Control
Employee-6034            22                0
Employee-6566            13                0
Employee-7350             1                0
...

======================================================================
Demo completed successfully!
  Shape: 4349 rows, 3 columns
======================================================================
```

## Project Structure

```
.
├── employee_query.py          # Quick demo script
├── interactive_walkthrough.py # Educational walkthrough script
├── visier_sdk_walkthrough.ipynb # Educational walkthrough notebook (recommended)
├── requirements.txt           # Python dependencies
├── visier.env.example        # Example environment variables
├── .env                      # Your credentials (not in git)
├── .gitignore               # Git ignore rules
└── README.md                 # This file
```

## Customization

### Changing the Time Period

Edit the `get_recent_month_timestamp()` function in `employee_query.py` to change the time period:

```python
def get_recent_month_timestamp() -> str:
    # Returns timestamp for first day of current month
    # Modify this to use a different date
    today = datetime.now()
    first_day = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    timestamp_ms = int(first_day.timestamp() * 1000)
    return str(timestamp_ms)
```

**Note:** If you get "No data returned", you may need to use a specific date that has data in your Visier tenant. You can hardcode a timestamp like:
```python
return "1735689600000"  # December 1, 2024 (example)
```

### Adding More Properties

Edit the `build_query_dto()` function to add more columns:

```python
"columns": [
    {"columnName": "Employee ID", "columnDefinition": {"property": {"name": "Employee.EmployeeID", "qualifyingPath": "Employee"}}},
    {"columnName": "Time in Role", "columnDefinition": {"property": {"name": "Employee.Time_in_Role", "qualifyingPath": "Employee"}}},
    # Add more columns here
]
```

## Troubleshooting

### "Missing required environment variables"
- Ensure your `.env` file exists and contains all required variables
- Check that variable names match exactly (case-sensitive)

### "Authentication failed"
- Verify your credentials are correct
- Check that your API key is valid
- Ensure your vanity name matches your tenant

### "No data returned"
- Verify the properties exist in your Visier tenant
- Check that you have permissions to access the Employee analytic object
- Try adjusting the time period

### "ModuleNotFoundError"
- Make sure you've activated your virtual environment
- Run `pip install -r requirements.txt` to install dependencies

## Resources

- [Visier Python SDK Documentation](https://github.com/visier/python-sdk)
- [Visier API Reference](https://documentation.visier.com/)
- [Visier API Samples](https://github.com/visier/api-samples)

## License

This project is provided as-is for educational purposes.
