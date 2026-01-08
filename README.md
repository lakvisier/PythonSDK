# Visier Python SDK - Employee Data Query

A simple, educational project demonstrating how to query employee data from the Visier Platform using the official Visier Python SDK.

## 🎯 Project Goals & Progress

### Primary Goal
> **📝 Placeholder for Primary Goal**  
> *The primary project goal will be documented here once shared. This section will outline the main objective we're working towards.*

### Progress Tracking
See [PROGRESS.md](./PROGRESS.md) for detailed progress tracking of completed work, work in progress, and planned features.

**Quick Status:**
- ✅ **Phase 1 Complete**: Basic list queries, interactive tutorials, and documentation
- 🚧 **Phase 2 Complete**: Aggregate query planning and analysis
- 📋 **Phase 3 Planned**: Aggregate query implementation
- 📋 **Phase 4 Planned**: Advanced features and utilities
- 📋 **Phase 5 Planned**: Comprehensive documentation and examples

## 🚀 Quick Start

Follow these simple steps to get started:

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

Or simply download and extract the ZIP file.

### 3. Create a Virtual Environment (Recommended)

**Option A: Using traditional `venv` and `pip` (Most Common)**

This is the standard Python approach that works everywhere:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Option B: Using `uv` (Modern Alternative)**

`uv` is a newer, faster Python package installer. If you have it installed (via Homebrew: `brew install uv`), you can use it:

```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

**Note:** `uv` is optional and not required. The traditional `venv` + `pip` method (Option A) works perfectly fine and is what most Python developers use.

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
   # Optional: Only required for specific operations
   VISIER_TENANT_CODE=tenant-code
   ```

   **⚠️ Important:** Never commit your `.env` file to version control. It's already in `.gitignore`.

   **Note:** The following packages will be installed from `requirements.txt`:
   - `visier-platform-sdk` - The Visier Python SDK
   - `python-dotenv` - For loading environment variables
   - `pandas` - For data analysis
   - `jupyter` - For running the notebook

### 5. Launch the Notebook

You can use either Jupyter Notebook or JupyterLab:

**Option A: Jupyter Notebook (Classic)**
```bash
jupyter notebook visier_sdk_walkthrough.ipynb
```

**Option B: JupyterLab (Modern Interface)**
```bash
jupyter lab visier_sdk_walkthrough.ipynb
```

This will open the notebook in your web browser. Follow along step by step!

## 📚 Learning Resources

### Interactive Notebook (Recommended)

**`visier_sdk_walkthrough.ipynb`** - Start here!

This Jupyter notebook provides a step-by-step walkthrough with:
- ✅ Clear explanations of each step
- ✅ Code examples you can run and modify
- ✅ Visual output showing results
- ✅ Educational content teaching SDK concepts
- ✅ Basic data analysis examples

**How to use:**
1. Open the notebook: `jupyter notebook visier_sdk_walkthrough.ipynb` (or use `jupyter lab`)
2. Run each cell in order (Shift+Enter)
3. Read the explanations and experiment with the code
4. Modify queries to explore different data

### Quick Demo Script

**`employee_query.py`** - For quick testing

A simple script that queries and displays employee data:
```bash
python employee_query.py
```

### Interactive Walkthrough Script

**`interactive_walkthrough.py`** - Command-line version

Same educational content as the notebook, but as a Python script:
```bash
python interactive_walkthrough.py
```

## 📖 What You'll Learn

By following the notebook, you'll learn how to:

1. **Configure the SDK** - Set up authentication and connection
2. **Create API Clients** - Understand how the SDK manages connections
3. **Build Queries** - Define what data you want to retrieve
4. **Execute Queries** - Send requests to Visier and get responses
5. **Process Results** - Convert API responses to usable formats
6. **Analyze Data** - Perform basic analysis on the retrieved data

## 🔍 Example Query

The notebook demonstrates querying employee data with:
- **EmployeeID** - Unique employee identifier
- **Time_in_Role** - How long the employee has been in their current role (months)
- **Span_Of_Control** - Number of direct reports

## 📁 Project Structure

```
.
├── visier_sdk_walkthrough.ipynb  # ⭐ Start here! Interactive notebook
├── employee_query.py              # Quick demo script
├── interactive_walkthrough.py     # Educational script version
├── AGGREGATE_QUERY_PLAN.md        # Implementation plan for aggregate queries
├── PROGRESS.md                    # Detailed progress tracking
├── requirements.txt               # Python dependencies
├── visier.env.example            # Environment variables template
├── .env                          # Your credentials (create this)
├── .gitignore                   # Git ignore rules
└── README.md                     # This file
```

## 🛠️ Troubleshooting

### "ModuleNotFoundError: No module named 'visier_platform_sdk'"

**Solution:** Make sure you've completed step 3 (Create Virtual Environment) which installs dependencies. If you skipped it or need to reinstall:

**Using traditional `pip` (most common):**
```bash
pip install -r requirements.txt
```

**Or using `uv` (if you have it installed):**
```bash
uv pip install -r requirements.txt
```

**Note:** Make sure your virtual environment is activated before running the scripts or notebook.

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
- The query uses December 1, 2024 as the time period
- If your tenant doesn't have data for that date, modify the timestamp in the notebook
- Check that the properties exist in your tenant

### "Jupyter not found" or "Jupyter Notebook won't start"

**Solution:** Make sure Jupyter is installed. It should already be installed from `requirements.txt` in step 3, but if needed:

**Using traditional `pip` (most common):**
```bash
pip install jupyter
jupyter notebook visier_sdk_walkthrough.ipynb
# Or use JupyterLab:
# jupyter lab visier_sdk_walkthrough.ipynb
```

**Or using `uv` (if you have it installed):**
```bash
uv pip install jupyter
jupyter notebook visier_sdk_walkthrough.ipynb
# Or use JupyterLab:
# jupyter lab visier_sdk_walkthrough.ipynb
```

**Note:** Make sure your virtual environment is activated:
```bash
source venv/bin/activate  # or source .venv/bin/activate if using uv
```

## 📝 Customization

### Changing the Time Period

In the notebook, find the query building cell and modify:
```python
'timeInterval': {'fromInstant': '1735689600000'}  # December 1, 2024
```

To use a different date, calculate the timestamp (in milliseconds):
```python
from datetime import datetime
date = datetime(2024, 11, 1)  # November 1, 2024
timestamp = str(int(date.timestamp() * 1000))  # Convert to milliseconds
```

### Adding More Properties

In the query building cell, add more columns to the `columns` array:
```python
{
    'columnName': 'Your Property Name',
    'columnDefinition': {
        'property': {
            'name': 'Employee.YourPropertyName',
            'qualifyingPath': 'Employee'
        }
    }
}
```

## 🔗 Resources

- [Visier Python SDK Documentation](https://github.com/visier/python-sdk)
- [Visier API Reference](https://documentation.visier.com/)
- [Visier API Samples](https://github.com/visier/api-samples)

## 💡 Tips

- **Start with the notebook** - It's the best way to learn
- **Run cells one at a time** - Don't rush, read the explanations
- **Experiment** - Try modifying the query to see what happens
- **Check the output** - Each cell shows you what's happening
- **Save your work** - The notebook saves automatically

## ✅ Success Checklist

Before you start, make sure you have:
- [ ] Python 3.9+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (from `requirements.txt` in step 3)
- [ ] `.env` file created with your Visier credentials (from step 4)
- [ ] Jupyter installed (included in `requirements.txt`)
- [ ] Notebook opens successfully

## 🎓 Next Steps

After completing the notebook:
1. Try modifying the query to get different properties
2. Experiment with different time periods
3. Explore other API methods (aggregate, snapshot)
4. Build your own queries for your use case
5. Check out the official SDK documentation for advanced features

---

**Ready to start?** Open `visier_sdk_walkthrough.ipynb` and follow along! 🚀
