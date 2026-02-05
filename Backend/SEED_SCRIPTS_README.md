# Database Seed Scripts

This directory contains seed scripts to populate your Compliance Hub database with compliance framework data.

## Available Seed Scripts

### 1. `seed_iso27001_clauses.py` - ISO 27001:2022 ISMS Requirements (Clauses 4-10)
**Run this FIRST!**

Populates the database with:
- ISO 27001:2022 ISMS Requirements framework
- All 27 mandatory requirements from Clauses 4-10:
  - Clause 4: Context of the organization (4 requirements)
  - Clause 5: Leadership (3 requirements)
  - Clause 6: Planning (5 requirements)
  - Clause 7: Support (7 requirements)
  - Clause 8: Operation (3 requirements)
  - Clause 9: Performance evaluation (3 requirements)
  - Clause 10: Improvement (2 requirements)

**These are MANDATORY for ISO 27001:2022 certification**

### 2. `seed_iso27001.py` - ISO 27001:2022 Annex A Controls
**Run this SECOND!**

Populates the database with:
- ISO 27001:2022 Annex A framework
- All 93 controls from Annex A
- Organized into 4 categories:
  - Organizational controls (37)
  - People controls (8)
  - Physical controls (14)
  - Technological controls (34)

**These are SELECTIVE based on risk assessment**

## How to Use

### Prerequisites
- Backend server must be set up
- PostgreSQL database must be running
- Virtual environment must be activated

### Running the Seed Script

1. **Navigate to your backend folder:**
```bash
cd C:\Users\dhank\compliance-hub-backend
```

2. **Activate virtual environment:**
```bash
venv\Scripts\activate
```

3. **Run BOTH seed scripts in this order:**

**First - ISMS Requirements (Mandatory):**
```bash
python seed_iso27001_clauses.py
```

**Second - Annex A Controls (Selective):**
```bash
python seed_iso27001.py
```

### Why This Order?

1. **ISMS Requirements (Clauses 4-10)** are the foundation - they define HOW you manage security
2. **Annex A Controls** are the specific security measures you implement

In an audit:
- Stage 1: Auditors verify you have an ISMS (Clauses 4-10)
- Stage 2: Auditors verify your selected controls work (Annex A)

### What Happens When You Run It

The script will:
1. ✅ Check if ISO 27001:2022 framework exists (create if not)
2. ✅ Check for existing controls (skip duplicates)
3. ✅ Create all 93 controls with:
   - Official control IDs (A.5.1, A.6.1, etc.)
   - Official titles
   - Full descriptions from the standard
   - Proper categorization
   - Priority levels
4. ✅ Display progress for each control created
5. ✅ Show summary statistics

### Expected Output

```
================================================================================
ISO 27001:2022 Database Seeding Script
================================================================================

Step 1: Creating ISO 27001:2022 framework...
✅ Created framework: ISO 27001:2022 (ID: 1)

Step 2: Creating all 93 ISO 27001:2022 controls...
✅ Created control: A.5.1 - Policies for information security
✅ Created control: A.5.2 - Information security roles and responsibilities
...
✅ Created control: A.8.34 - Protection of information systems during audit testing

================================================================================
✅ Successfully created 93 controls
================================================================================

🎉 ISO 27001:2022 seeding completed successfully!
================================================================================

📊 Summary:
   Framework: ISO 27001:2022
   Total Controls: 93
   Categories:
     - Organizational controls: 37
     - People controls: 8
     - Physical controls: 14
     - Technological controls: 34
```

## Re-running the Script

If you run the script again:
- ✅ It will skip existing framework
- ✅ It will skip existing controls
- ✅ It will only create missing controls (if any)
- ✅ Safe to run multiple times

## Verifying the Data

After running the seed script, verify in:

### 1. API Documentation (http://localhost:8000/docs)
- Use `GET /api/v1/frameworks/` to see the framework
- Use `GET /api/v1/controls/` to see all controls
- Use `GET /api/v1/frameworks/1/stats` to see statistics

### 2. pgAdmin
- Navigate to: compliance_hub → public → Tables → controls
- Right-click → View/Edit Data → First 100 Rows
- You should see all 93 controls

### 3. Test with Frontend
- Once frontend is connected, all controls will appear in the Controls tab
- Dashboard will show real compliance metrics

## Customization

If you want to customize the controls:
1. Edit `seed_iso27001.py`
2. Modify the `controls_data` array
3. Re-run the script (existing controls will be skipped)

## Next Steps

After seeding ISO 27001:2022:
1. ✅ Run `seed_soc2.py` (when created) for SOC 2 controls
2. ✅ Connect frontend to backend
3. ✅ Start assigning controls to users
4. ✅ Begin adding evidence to controls

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'app'"
**Solution:** Make sure you're in the `compliance-hub-backend` folder and virtual environment is activated.

### Error: "Could not connect to database"
**Solution:** Make sure PostgreSQL is running and your `.env` file has the correct DATABASE_URL.

### Warning: "Found X existing controls"
**Solution:** This is normal if you've run the script before. The script will skip existing controls.

## Data Source

All control data is sourced from:
- ISO/IEC 27001:2022 Information Security, Cybersecurity and Privacy Protection
- Official control objectives and descriptions from Annex A

## Need Help?

If you encounter issues:
1. Check that the backend server can start (`uvicorn app.main:app --reload`)
2. Verify database connection in `.env` file
3. Check PostgreSQL is running in pgAdmin
4. Review the error message in the terminal
