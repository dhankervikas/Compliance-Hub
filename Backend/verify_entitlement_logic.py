
from app.database import SessionLocal
from app.models.tenant import Tenant
from app.models.tenant_feature import TenantFeature
from app.models.tenant_framework import TenantFramework
from app.models.framework import Framework

def verify():
    db = SessionLocal()
    
    tenant_slug = "testtest"
    print(f"Checking Plan for: {tenant_slug}")
    
    # 1. Resolve Tenant
    tenant = db.query(Tenant).filter(Tenant.slug == tenant_slug).first()
    if not tenant:
        print("Tenant not found!")
        return
        
    print(f"Internal ID: {tenant.internal_tenant_id}")
    
    # 2. Check Feature Logic (Simulate FeatureGuard)
    feature_key = "aws_scanner"
    print(f"\nChecking Feature: {feature_key}")
    feature = db.query(TenantFeature).filter(
        TenantFeature.tenant_id == tenant.internal_tenant_id,
        TenantFeature.feature_key == feature_key,
        TenantFeature.is_active == True
    ).first()
    
    if feature:
        print(f" -> ALLOWED (Feature Active)")
    else:
        print(f" -> DENIED (Feature Missing or Inactive)")
        
    # 3. Check Framework Logic (Simulate FrameworkGuard)
    fw_code = "ISO27001"
    print(f"\nChecking Framework: {fw_code}")
    link = db.query(TenantFramework).join(Framework).filter(
        TenantFramework.tenant_id == tenant.internal_tenant_id,
        Framework.code == fw_code,
        TenantFramework.is_active == True
    ).first()
    
    if link:
         print(f" -> ALLOWED (Framework Active)")
    else:
         print(f" -> DENIED (Framework Missing or Inactive)")

    db.close()

if __name__ == "__main__":
    verify()
