
from app.database import engine, Base
from app.models.tenant import Tenant
from app.models.tenant_framework import TenantFramework
from app.models.tenant_feature import TenantFeature
# Import other models to ensure they are registered if needed, but Base.metadata.create_all usually handles strictly imported ones.

print("Creating all missing tables...")
Base.metadata.create_all(bind=engine)
print("Tables created.")
