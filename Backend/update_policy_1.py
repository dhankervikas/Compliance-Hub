import os
import sys

# Add current directory to path
sys.path.append(os.getcwd())

from app.database import SessionLocal
from app.models.policy import Policy

NEW_CONTENT = """
| Document Control | |
| :--- | :--- |
| **Classification** | Internal Use Only |
| **Owner** | CISO |
| **Approver** | CEO |
| **Version** | 1.0 (Live) |
| **Last Updated** | Feb 28, 2023 |

---

# Information Security Policy

## 1. Purpose
The purpose of this Information Security Policy is to protect the information assets of the organization from all threats, whether internal or external, deliberate or accidental.

## 2. Scope
This policy applies to all employees, contractors, and third-party users who have access to information systems and data.

## 3. Policy Statements

### 3.1 Information Security Objectives
The organization shall define information security objectives that are consistent with the strategic direction of the organization.

- **Confidentiality**: Ensuring that information is accessible only to those authorized to have access.
- **Integrity**: Safeguarding the accuracy and completeness of information and processing methods.
- **Availability**: Ensuring that authorized users have access to information and associated assets when required.

### 3.2 Roles and Responsibilities
- **Chief Information Security Officer (CISO)**: Responsible for the overall management of the Information Security Management System (ISMS).
- **All Employees**: Responsible for complying with this policy and reporting security incidents.

## 4. Compliance Mapping
| ISO 27001 Requirement | Policy Section |
| :--- | :--- |
| A.5.1 Policies for information security | Section 3 |
| A.6.1.1 Information security roles and responsibilities | Section 3.2 |
"""

def update_policy_one():
    print("Connecting to DB...")
    db = SessionLocal()
    try:
        print("Fetching Policy 1...")
        policy = db.query(Policy).filter(Policy.id == 1).first()
        if policy:
            print("Updating content...")
            policy.content = NEW_CONTENT
            db.commit()
            print("Update complete.")
        else:
            print("Policy 1 not found.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    update_policy_one()
