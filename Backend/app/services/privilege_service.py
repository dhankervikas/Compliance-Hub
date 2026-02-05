from sqlalchemy.orm import Session
from app.models.person import Person, EmploymentStatus, SourceType
from app.models.user import User
from app.schemas.person import PersonCreate
from datetime import datetime
from typing import List, Dict, Any

class PrivilegeService:
    
    @staticmethod
    def import_people(db: Session, tenant_id: str, people_data: List[Dict[str, Any]], source: str = SourceType.MANUAL_IMPORT):
        """
        Syncs external people data into the Person table.
        Acts as an upsert based on Email.
        """
        stats = {"created": 0, "updated": 0, "errors": 0}
        
        for p_data in people_data:
            try:
                email = p_data.get("email")
                if not email:
                    continue
                    
                # Normalize email
                email = email.lower().strip()
                
                # Check existence
                person = db.query(Person).filter(
                    Person.email == email, 
                    Person.tenant_id == tenant_id
                ).first()
                
                if person:
                    # Update
                    person.full_name = p_data.get("full_name", person.full_name)
                    person.job_title = p_data.get("job_title", person.job_title)
                    person.department = p_data.get("department", person.department)
                    person.employment_status = p_data.get("employment_status", person.employment_status)
                    person.external_id = p_data.get("external_id", person.external_id)
                    person.source = source
                    person.last_synced_at = datetime.utcnow()
                    stats["updated"] += 1
                else:
                    # Create
                    new_person = Person(
                        tenant_id=tenant_id,
                        email=email,
                        full_name=p_data.get("full_name"),
                        job_title=p_data.get("job_title"),
                        department=p_data.get("department"),
                        employment_status=p_data.get("employment_status", EmploymentStatus.ACTIVE),
                        external_id=p_data.get("external_id"),
                        source=source
                    )
                    db.add(new_person)
                    stats["created"] += 1
                    
            except Exception as e:
                print(f"Error importing person {p_data.get('email')}: {e}")
                stats["errors"] += 1
                
        db.commit()
        return stats

    @staticmethod
    def detect_zombie_accounts(db: Session, tenant_id: str) -> List[Dict]:
        """
        Identifies Compliance Risks:
        Active System Users who are marked as Inactive in HR Data (People).
        """
        # 1. Get all Inactive People
        inactive_people = db.query(Person).filter(
            Person.tenant_id == tenant_id,
            Person.employment_status == EmploymentStatus.INACTIVE
        ).all()
        
        zombies = []
        
        for p in inactive_people:
            # 2. Check for Active User Account with same email
            user = db.query(User).filter(
                User.tenant_id == tenant_id,
                User.email == p.email,
                User.is_active == True
            ).first()
            
            if user:
                zombies.append({
                    "risk_level": "CRITICAL",
                    "description": "Terminated employee retains active system access",
                    "person": {
                        "name": p.full_name,
                        "email": p.email,
                        "terminated_date": p.last_synced_at 
                    },
                    "user_account": {
                        "id": user.id,
                        "username": user.username,
                        "last_login": None # Could add this to User model later
                    },
                    "framework_mapping": ["ISO 27001:2013 A.9.2.6", "SOC 2 CC5.1"]
                })
                
        return zombies
