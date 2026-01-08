# Visier Python SDK - Data Query Project

A project demonstrating how to query data from the Visier Platform using both the official Visier Python SDK (for detailed queries) and RESTful API (for aggregate queries).

## 🎯 Project Goals & Progress

### Primary Goal
> **📝 Placeholder for Primary Goal**  
> *The primary project goal will be documented here once shared. This section will outline the main objective we're working towards.*

### Progress Tracking
See [PROGRESS.md](./PROGRESS.md) for detailed progress tracking of completed work, work in progress, and planned features.

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
│   ├── example_simple_query.py     # Simple query examples
│   ├── example_batch_query.py      # Batch query examples
│   ├── output/                      # CSV output files directory
│   ├── VANILLA_AGGREGATE_USAGE.md  # Single metric guide
│   ├── BATCH_QUERY_GUIDE.md        # Batch query guide (50+ metrics)
│   ├── AGGREGATE_QUERY_API_REFERENCE.md  # Full API schema reference
│   └── AGGREGATE_QUERY_PLAN.md           # Implementation plan
│
├── archive/                      # Deprecated implementations
│   ├── aggregate_query.py        # Old SDK-based aggregate (deprecated)
│   └── metric_discovery.py       # Metric discovery (not needed)
│
├── PROGRESS.md                       # Progress tracking
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

**Single Metric:**
```python
from aggregate.aggregate_query_vanilla import query_metric

# Simple query - last 6 months by Function
df = query_metric("employeeCount", dimensions=["Function"])

# Save to CSV
df = query_metric("employeeCount", dimensions=["Function"], save_csv="results.csv")
```

**Batch Query (50+ Metrics):**
```python
from aggregate.aggregate_query_vanilla import (
    query_multiple_metrics,
    create_selection_concept_filter
)

# Your 50 metrics
metric_ids = ["employeeCount", "turnoverRate", "headcount", ...]

# Query all with same dimensions and filters
df = query_multiple_metrics(
    metric_ids=metric_ids,
    dimensions=["Function", "Gender"],
    dimension_member_filters={"Function": ["Engineering", "Sales"]},
    global_filters=[create_selection_concept_filter("isActive")],
    save_csv="all_metrics.csv"
)
```

**Run Examples:**
```bash
# Simple query example
python aggregate/example_simple_query.py

# Batch query example
python aggregate/example_batch_query.py
```

**Features:**
- ✅ Simple `query_metric()` function
- ✅ Batch queries: `query_multiple_metrics()` for 50+ metrics
- ✅ Dimension member filtering (focus on specific members)
- ✅ Global filters (apply across all metrics)
- ✅ Automatic time period handling
- ✅ Direct CSV export
- ✅ No SDK dependencies - pure HTTP requests

**Documentation:**
- [`aggregate/VANILLA_AGGREGATE_USAGE.md`](./aggregate/VANILLA_AGGREGATE_USAGE.md) - Single metric guide
- [`aggregate/BATCH_QUERY_GUIDE.md`](./aggregate/BATCH_QUERY_GUIDE.md) - Batch query guide (50+ metrics)

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
- **Usage Guide**: [`aggregate/VANILLA_AGGREGATE_USAGE.md`](./aggregate/VANILLA_AGGREGATE_USAGE.md) - Single metric queries
- **Batch Guide**: [`aggregate/BATCH_QUERY_GUIDE.md`](./aggregate/BATCH_QUERY_GUIDE.md) - Batch queries (50+ metrics)
- **API Reference**: [`aggregate/AGGREGATE_QUERY_API_REFERENCE.md`](./aggregate/AGGREGATE_QUERY_API_REFERENCE.md) - Full API schema
- **Implementation Plan**: [`aggregate/AGGREGATE_QUERY_PLAN.md`](./aggregate/AGGREGATE_QUERY_PLAN.md) - Development plan

### Reference
- **Progress Tracking**: [`PROGRESS.md`](./PROGRESS.md) - Project progress

## 🔗 Resources

- [Visier Python SDK Documentation](https://github.com/visier/python-sdk)
- [Visier API Reference](https://documentation.visier.com/)
- [Visier API Samples](https://github.com/visier/api-samples)
- [Visier Alpine Platform Postman Collection](https://www.postman.com/visier-alpine/visier-alpine-platform/overview) - API examples and authentication flow
- [Data Query API Documentation](https://www.postman.com/visier-alpine/visier-alpine-platform/documentation/baicg0u/data-query-api?entity=request-26533916-2f770879-3235-4bfc-991f-215f68513200)

## 📋 Roadmap

See [`PRODUCTIFICATION_ROADMAP.md`](./PRODUCTIFICATION_ROADMAP.md) for the complete roadmap to productify the Visier Alpine Platform Postman Collection into a production-ready Python workflow.

## 💡 Tips

- **For detailed queries**: Start with `sdk/visier_sdk_walkthrough.ipynb`
- **For aggregate metrics**: Use `aggregate/aggregate_query_vanilla.py`
- **For batch queries**: See `aggregate/BATCH_QUERY_GUIDE.md`
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
- **For aggregate queries**: See `aggregate/VANILLA_AGGREGATE_USAGE.md` 📊
