# Visier Python SDK - Data Query Project

A project demonstrating how to query data from the Visier Platform using both the official Visier Python SDK (for detailed queries) and RESTful API (for aggregate queries).

## 🎯 Project Goals & Progress

### Primary Goal
> **📝 Placeholder for Primary Goal**  
> *The primary project goal will be documented here once shared. This section will outline the main objective we're working towards.*

### Progress Tracking
See [docs/planning/PROGRESS.md](./docs/planning/PROGRESS.md) for detailed progress tracking of completed work, work in progress, and planned features.

**Quick Status:**
- ✅ **SDK Module Complete**: Detailed list queries, interactive tutorials, and documentation
- ✅ **Aggregate Module Complete**: RESTful aggregate queries with batch support (50+ metrics)
- 📋 **Future**: Advanced features and utilities (pivot tables, visualization)

## 📁 Project Structure

This project is organized into two main modules:

```
.
├── sdk/                          # SDK-based detailed queries
│   ├── employee_query.py         # Quick demo script
│   ├── interactive_walkthrough.py # Educational script
│   └── visier_sdk_walkthrough.ipynb # ⭐ Interactive notebook
│
├── aggregate/                    # RESTful aggregate queries (no SDK)
│   ├── aggregate_query_vanilla.py  # Main aggregate query module
│   ├── scripts/                    # CLI tools and utilities
│   │   ├── run_query.py            # CLI tool for running queries
│   │   └── discover_dimension_levels.py  # Dimension level discovery
│   ├── examples/                   # Example query payloads
│   │   ├── query_payload_examples.json
│   │   └── query_payload_examples_org_hierarchy.json
│   ├── docs/                       # Documentation
│   │   ├── README.md               # Usage guide
│   │   └── LEARNINGS.md            # Query patterns and learnings
│   ├── tests/                      # Test scripts
│   └── output/                     # CSV output files directory
│
├── docs/                             # Documentation and planning
│   ├── api/                          # API specifications
│   │   └── openapi.json              # OpenAPI 3.0 specification
│   └── planning/                     # Planning documents and roadmaps
├── visier-sdk-source/                # Visier SDK source code (reference)
├── requirements.txt                  # Python dependencies
├── visier.env.example                # Environment variables template
└── README.md                         # This file
```

## 🚀 Quick Start

### 1. Install Python

Make sure you have Python 3.9 or higher installed:
```bash
python3 --version
```

### 2. Clone or Download This Repository

```bash
git clone <repository-url>
cd PythonSDK
```

### 3. Create a Virtual Environment (Recommended)

**Option A: Using traditional `venv` and `pip` (Most Common)**

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Option B: Using `uv` (Modern Alternative)**

```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

### 4. Configure Your Credentials

1. Copy the example environment file:
   ```bash
   cp visier.env.example .env
   ```

2. Edit `.env` with your Visier credentials:
   ```env
   VISIER_HOST=https://your-tenant.api.visier.io
   VISIER_APIKEY=your-api-key
   VISIER_VANITY=your-vanity-name
   VISIER_USERNAME=your-username
   VISIER_PASSWORD=your-password
   ```

   **⚠️ Important:** Never commit your `.env` file to version control.

## 📚 Two Ways to Query Data

### 1. SDK Module: Detailed Queries

**Location:** `sdk/` directory

Use the official Visier Python SDK for detailed list queries (employee records, properties, etc.).

**Quick Start:**
```bash
# Interactive notebook (recommended)
jupyter notebook sdk/visier_sdk_walkthrough.ipynb

# Or quick demo script
python sdk/employee_query.py

# Or interactive walkthrough script
python sdk/interactive_walkthrough.py
```

**What you'll learn:**
- Configure the SDK
- Create API clients
- Build list queries
- Execute queries and process results
- Analyze detailed employee data

**Use cases:**
- Get detailed employee records
- Query specific properties
- List queries with filters
- Educational/tutorial purposes

### 2. Aggregate Module: RESTful Aggregate Queries

**Location:** `aggregate/` directory

Use RESTful API calls (no SDK) for aggregate metric queries. Perfect for batch queries of 50+ metrics.

**Quick Start:**

**Using the CLI Tool:**
```bash
# Run query from JSON payload file
python aggregate/scripts/run_query.py --file aggregate/examples/query_payload_examples.json
```

**Using Python API:**
```python
from aggregate.aggregate_query_vanilla import (
    execute_vanilla_aggregate_query,
    convert_vanilla_response_to_dataframe,
    create_dimension_axis
)

# Build query
axes = [create_dimension_axis("Function")]
response = execute_vanilla_aggregate_query(metric_id="employeeCount", axes=axes)
df = convert_vanilla_response_to_dataframe(response, metric_id="employeeCount")
```

**Run Query:**
```bash
# Run query from JSON payload file
python aggregate/scripts/run_query.py --file aggregate/examples/query_payload_examples.json

# Or use the default payload
python aggregate/scripts/run_query.py
```

**Features:**
- ✅ RESTful API queries (no SDK dependencies)
- ✅ Helper functions for building queries
- ✅ Dimension member filtering
- ✅ Time interval support
- ✅ Direct CSV export via CLI tool
- ✅ JSON payload-based queries

**Documentation:**
- [`aggregate/README.md`](./aggregate/README.md) - Complete usage guide
- [`aggregate/LEARNINGS.md`](./aggregate/LEARNINGS.md) - Query patterns and learnings

**Use cases:**
- Query aggregated metrics (employeeCount, turnoverRate, etc.)
- Batch query 50+ metrics efficiently
- Group by dimensions (Function, Gender, etc.)
- Apply filters across multiple metrics
- Export to CSV for analysis

## 🔍 Which Module Should I Use?

| Use Case | Module | Example |
|----------|--------|---------|
| Get detailed employee records | SDK (`sdk/`) | List all employees with properties |
| Query aggregated metrics | Aggregate (`aggregate/`) | Employee count by department |
| Batch query 50+ metrics | Aggregate (`aggregate/`) | Multiple metrics with shared filters |
| Educational/tutorial | SDK (`sdk/`) | Learn SDK concepts |
| Production metric queries | Aggregate (`aggregate/`) | RESTful, no SDK dependencies |

## 🛠️ Troubleshooting

### "ModuleNotFoundError: No module named 'visier_platform_sdk'"

**Solution:** Make sure you've activated your virtual environment and installed dependencies:
```bash
source venv/bin/activate  # or source .venv/bin/activate if using uv
pip install -r requirements.txt
```

### "Missing required environment variables"

**Solution:** 
1. Make sure you've created `.env` from `visier.env.example`
2. Fill in all required variables with your Visier credentials
3. Check that variable names match exactly (case-sensitive)

### "Authentication failed"

**Solution:**
- Verify your credentials in `.env` file
- Check that `VISIER_VANITY` matches your tenant
- Ensure `VISIER_APIKEY` is set correctly

### "No data returned"

**Solution:**
- Check that the metric IDs exist in your tenant
- Verify the time period has data
- Ensure you have permissions for the data

## 📖 Documentation

### SDK Module
- **Interactive Notebook**: `sdk/visier_sdk_walkthrough.ipynb` - Start here for SDK learning
- **Quick Demo**: `sdk/employee_query.py` - Simple list query example
- **Walkthrough**: `sdk/interactive_walkthrough.py` - Command-line tutorial

### Aggregate Module
- **Usage Guide**: [`aggregate/README.md`](./aggregate/README.md) - Complete usage guide and examples
- **Learnings**: [`aggregate/LEARNINGS.md`](./aggregate/LEARNINGS.md) - Query patterns, time intervals, and best practices
- **API Reference**: [`docs/api/openapi.json`](./docs/api/openapi.json) - OpenAPI specification

### Reference
- **Progress Tracking**: [`docs/planning/PROGRESS.md`](./docs/planning/PROGRESS.md) - Project progress

## 🔗 Resources

- [Visier Python SDK Documentation](https://github.com/visier/python-sdk)
- [Visier API Reference](https://documentation.visier.com/)
- [Visier API Samples](https://github.com/visier/api-samples)
- [Visier Alpine Platform Postman Collection](https://www.postman.com/visier-alpine/visier-alpine-platform/overview) - API examples and authentication flow
- [Data Query API Documentation](https://www.postman.com/visier-alpine/visier-alpine-platform/documentation/baicg0u/data-query-api?entity=request-26533916-2f770879-3235-4bfc-991f-215f68513200)

## 📋 Roadmap

See [`docs/planning/PRODUCTIFICATION_ROADMAP.md`](./docs/planning/PRODUCTIFICATION_ROADMAP.md) for the complete roadmap to productify the Visier Alpine Platform Postman Collection into a production-ready Python workflow.

## 💡 Tips

- **For detailed queries**: Start with `sdk/visier_sdk_walkthrough.ipynb`
- **For aggregate metrics**: Use `aggregate/scripts/run_query.py` or `aggregate/aggregate_query_vanilla.py`
- **For query patterns**: See `aggregate/LEARNINGS.md`
- **Experiment**: Try modifying queries to see what happens
- **Check output**: Each script shows what's happening

## ✅ Success Checklist

Before you start, make sure you have:
- [ ] Python 3.9+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created with your Visier credentials
- [ ] Jupyter installed (for SDK notebook, included in `requirements.txt`)

---

**Ready to start?**

- **For detailed queries**: Open `sdk/visier_sdk_walkthrough.ipynb` 🚀
- **For aggregate queries**: See `aggregate/README.md` 📊
