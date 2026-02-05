import sys
import os
import requests
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from app.database import Base, SessionLocal
from app.models.user import User
from app.models.cloud_resource import CloudResource
from app.models.compliance_result import ComplianceResult
from app.services.compliance_evaluator import ComplianceEvaluator

# Colors
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"

def print_header(title):
    print(f"\n{BOLD}=== {title} ==={RESET}")

def check_db_connection():
    print_header("1. Checking Database Connectivity")
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        print(f"{GREEN}PASS: Database Connection Successful{RESET}")
        db.close()
        return True
    except Exception as e:
        print(f"{RED}FAIL: Database Connection Failed: {e}{RESET}")
        return False

def list_tenants():
    print_header("2. Tenants Overview (Tenants You Have)")
    db = SessionLocal()
    results = db.query(User.tenant_id, func.count(User.id)).group_by(User.tenant_id).all()
    
    if not results:
        print(f"{RED}No tenants found (checking 'users' table).{RESET}")
    else:
        print(f"{'Tenant ID':<30} | {'Users':<10}")
        print("-" * 45)
        for tenant_id, count in results:
            print(f"{tenant_id:<30} | {count:<10}")
    db.close()

def run_evaluator_check():
    print_header("3. Compliance Evaluator & Dashboard Data")
    db = SessionLocal()
    
    # Check Controls
    result_count = db.query(ComplianceResult).count()
    print(f"Total Compliance Results: {result_count}")
    
    if result_count == 0:
        print(f"{RED}WARNING: No compliance results found. Dashboard will be empty.{RESET}")
        print("Run 'python seed_compliance_results.py' to generate data.")
    else:
        print(f"{GREEN}PASS: Compliance Results found. Dashboard should populate.{RESET}")
        
        # Sample Check
        sample = db.query(ComplianceResult).first()
        print(f"Sample Result: Control {sample.control_id} ({sample.status}) for Tenant '{sample.tenant_id}'")

    db.close()

def api_check_instructions():
    print_header("4. Manual Verification Steps")
    print("To fully verify the system, perform these manual steps:")
    
    print("\n   [A] Verify Dashboard (Frontend)")
    print("       1. Start Backend:  uvicorn app.main:app --reload")
    print("       2. Start Frontend: npm start")
    print("       3. Login as 'admin' / 'admin123'")
    print("       4. Navigate to http://localhost:3000/compliance-dashboard")
    print("       5. VERIFY: You see 3 Summary Cards and a Domain List.")
    
    print("\n   [B] Verify Tenant Isolation")
    print("       1. Run 'python verify_multitenancy.py'")
    print("       2. VERIFY: Script reports PASS for both Admin and Tenant visibility.")

    print("\n   [C] Create New Tenant")
    print("       1. Go to http://localhost:3000/workspaces")
    print("       2. Click 'Create New Workspace'")
    print("       3. Verify new tile appears and you can login to it.")

if __name__ == "__main__":
    if check_db_connection():
        list_tenants()
        run_evaluator_check()
        api_check_instructions()
