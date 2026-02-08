import os
print(f"=== DATABASE_URL: {os.environ.get('DATABASE_URL', 'NOT SET')} ===")
from fastapi import FastAPI, Depends
print("!!! LOADER DEBUG: MAIN.PY LOADED !!!")
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base, get_db
from app.models import User, Framework, Control, Evidence, Policy, Assessment, Document
from app.api import policy_generation
from app.api import requirements
from app.api import auth, frameworks, controls, evidence, automated_tests, policies, assessments, analytics, processes, ai, diagnostic, reports, audits, context, settings as compliance_settings, master_templates, users, compliance, people, auditor_portal

# Create database tables
Base.metadata.create_all(bind=engine)


from app.api.deps import verify_tenant, verify_auditor_permissions

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Compliance Management System API",
    dependencies=[Depends(verify_tenant), Depends(verify_auditor_permissions)],
    debug=True # FORCE DEBUG FOR TRACEBACK
)

from app.api import health
app.include_router(health.router, prefix=f"{settings.API_V1_PREFIX}/health", tags=["System Health"])
app.include_router(auditor_portal.router, prefix=f"{settings.API_V1_PREFIX}", tags=["Auditor Portal"])

# Configure CORS
# Configure CORS


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS, # Use settings
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response

# ForcePreflightMiddleware removed - relying on CORSMiddleware and verify_tenant bypass

from fastapi import Request
from fastapi.responses import JSONResponse

# Global Options Handler moved to bottom to prevent shadowing
# @app.options("/{path:path}") passed manually at end

@app.exception_handler(Exception)
async def validation_exception_handler(request, exc):
    import traceback
    error_msg = traceback.format_exc()
    print(f"CRITICAL 500 ERROR: {error_msg}")
    response = JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
    origin = request.headers.get("origin", "")
    if origin:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
    return response

from app.utils.security import get_password_hash
from app.database import SessionLocal 

@app.on_event("startup")
def startup_event():
    """
    Initialize database and create initial admin user if not exists.
    This fixes the issue with ephemeral databases (Render) wiping data on restart.
    """
    db = SessionLocal()
    try:
        # Check for admin user
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            print("[STARTUP] Admin user not found. Creating default admin...")
            admin_user = User(
                email="admin@assurisk.ai",
                username="admin",
                full_name="System Administrator",
                hashed_password=get_password_hash("admin123"),
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            print("[STARTUP] Admin user 'admin' created successfully.")
        else:
            print("[STARTUP] Admin user already exists. Checking/Resetting password...")
            # Force reset password to ensure access if locked out
            admin.hashed_password = get_password_hash("admin123")
            db.commit()
            print("[STARTUP] Admin password reset to 'admin123'.")
            
    except Exception as e:
        print(f"[STARTUP ERROR] Failed to initialize data: {e}")
    finally:
        db.close()

    # --- AUTO-SEED SOC 2 FIX ---
    # This runs outside the main try block to ensure independent failure handling
    try:
        from app.models import Control
        from seed_soc2_unified import CONTROLS_DATA
        
        db_seed = SessionLocal()
        soc2_count = db_seed.query(Control).filter(Control.control_id.like("CC%")).count()
        print(f"[STARTUP] Checking SOC 2 Controls... Count: {soc2_count}")
        
        # If count is suspicious (e.g. absent or partial old seed), re-seed
        # Target is ~61 controls. If < 50, we assume it needs repair.
        if soc2_count < 50:
            print("[STARTUP] SOC 2 Controls appear incomplete or missing. Running Auto-Seed...")
            from seed_soc2_unified import seed_soc2_unified
            seed_soc2_unified() # This script handles its own DB session
            print("[STARTUP] SOC 2 Auto-Seed Complete.")
        else:
            print("[STARTUP] SOC 2 Data appears healthy.")
        
        db_seed.close()

        # --- RUN MASTER SEEDER FOR OTHER FRAMEWORKS ---
        from app.services.startup_seeder import run_startup_seed
        print("[STARTUP] Running Master Framework Seeder...")
        run_startup_seed()

    except Exception as e:
        print(f"[STARTUP ERROR] Failed to auto-seed SOC 2 or Frameworks: {e}")

print("[OK] CORS CONFIGURATION LOADED: Allowed access from localhost:3000 and localhost:3001")



@app.get("/")
async def root():
    """Serve React frontend or API welcome"""
    import os
    from fastapi.responses import FileResponse
    index_path = os.path.join(os.path.dirname(__file__), "..", "static_frontend", "index.html")
    index_path = os.path.abspath(index_path)
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "message": "Welcome to Compliance Hub API",
        "version": settings.VERSION,
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME
    }


# Include API routers
app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["Authentication"])
app.include_router(frameworks.router, prefix=f"{settings.API_V1_PREFIX}/frameworks", tags=["Frameworks"])
app.include_router(controls.router, prefix=f"{settings.API_V1_PREFIX}/controls", tags=["Controls"])
app.include_router(evidence.router, prefix=f"{settings.API_V1_PREFIX}/evidence", tags=["Evidence"])
app.include_router(automated_tests.router, prefix=f"{settings.API_V1_PREFIX}/automated-tests", tags=["Automated Tests"])
app.include_router(policies.router, prefix=f"{settings.API_V1_PREFIX}/policies", tags=["Policies"])
app.include_router(assessments.router, prefix=f"{settings.API_V1_PREFIX}/assessments", tags=["Assessments"])
app.include_router(analytics.router, prefix=f"{settings.API_V1_PREFIX}/analytics", tags=["Analytics"])
app.include_router(processes.router, prefix=f"{settings.API_V1_PREFIX}/processes", tags=["Processes"])
app.include_router(ai.router, prefix=f"{settings.API_V1_PREFIX}/ai", tags=["AI"])
app.include_router(diagnostic.router, prefix=f"{settings.API_V1_PREFIX}/diagnostic", tags=["Diagnostic"])
app.include_router(reports.router, prefix=f"{settings.API_V1_PREFIX}/reports", tags=["Reports"])
app.include_router(reports.router, prefix=f"{settings.API_V1_PREFIX}/reports", tags=["Reports"])
app.include_router(audits.router, prefix=f"{settings.API_V1_PREFIX}/audits", tags=["Audits"])
app.include_router(compliance_settings.router, prefix=f"{settings.API_V1_PREFIX}/settings", tags=["Compliance Settings"])
app.include_router(context.router, prefix=f"{settings.API_V1_PREFIX}/context", tags=["Context (Clause 4)"])
app.include_router(master_templates.router, prefix=f"{settings.API_V1_PREFIX}/master-templates", tags=["Master Templates"])
app.include_router(users.router, prefix=f"{settings.API_V1_PREFIX}/users", tags=["User Management"])
app.include_router(compliance.router, prefix=f"{settings.API_V1_PREFIX}/compliance", tags=["AI Compliance"])
app.include_router(people.router, prefix=f"{settings.API_V1_PREFIX}/people", tags=["Identity & People"])
from app.api import tenants
app.include_router(tenants.router, prefix=f"{settings.API_V1_PREFIX}/super-admin/tenants", tags=["Tenant Management"])

from app.api import scope
app.include_router(scope.router, prefix=f"{settings.API_V1_PREFIX}/scope", tags=["Scope Management"])
from app.api import cloud_resources, compliance_summary
# app.include_router(health.router, prefix="/health-api", tags=["System Health"])
# Force Reload Trigger 8 (Final)
app.include_router(compliance_summary.router, prefix=settings.API_V1_PREFIX, tags=["Compliance Summary"])
# Force Reload Trigger 4

# Policy Generation Router
app.include_router(
    policy_generation.router,
    prefix="/api",
    tags=["Policy Generation"]
)

# Requirements / Dynamic AI Router
app.include_router(
    requirements.router,
    prefix=settings.API_V1_PREFIX,
    tags=["Requirements"]
)

# MOUNT STATIC FILES FOR REPORTS AND SERVE REACT FRONTEND
try:
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse
    import os
    
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
    app.mount("/api-static", StaticFiles(directory=static_dir), name="static")

    # SERVE REACT FRONTEND
    frontend_dir = os.path.join(os.path.dirname(__file__), "..", "static_frontend")
    frontend_dir = os.path.abspath(frontend_dir)
    
    if os.path.exists(frontend_dir):
        react_static = os.path.join(frontend_dir, "static")
        if os.path.exists(react_static):
            app.mount("/static", StaticFiles(directory=react_static), name="react-static")
        
        @app.get("/{full_path:path}")
        async def serve_react(full_path: str):
            if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("openapi"):
                return None
            file_path = os.path.join(frontend_dir, full_path)
            if os.path.isfile(file_path):
                return FileResponse(file_path)
            return FileResponse(os.path.join(frontend_dir, "index.html"))
        
        print(f"[STARTUP] React frontend mounted from: {frontend_dir}")
    else:
        print(f"[STARTUP] No frontend build found at: {frontend_dir}")

except Exception as e:
    print(f"Warning: Could not mount static/frontend directory: {e}")

@app.get("/api/v1/health-debug")
def health_debug():
    return {"status": "debug-ok"}

@app.get("/force-seed-public")
def force_seed_public():
    """
    Temporary endpoint to force DB seeding in Prod if startup event failed.
    """
    try:
        from app.services.startup_seeder import run_startup_seed
        run_startup_seed()
        return {"status": "success", "message": "Seeding completed successfully."}
    except Exception as e:
        import traceback
        return {"status": "error", "message": str(e), "traceback": traceback.format_exc()}


@app.get("/db-stats-public")

def get_stats_public(db: SessionLocal = Depends(get_db)):
    from app.models.framework import Framework
    from app.models.control import Control
    frameworks = db.query(Framework).all()
    stats = []
    total_controls = 0
    for fw in frameworks:
        count = db.query(Control).filter(Control.framework_id == fw.id).count()
        total_controls += count
        stats.append({"id": fw.id, "code": fw.code, "name": fw.name, "count": count})
    return {"frameworks": stats, "total": total_controls}

# MOVED: Global Options Handler (Catch-All)
# Must be Last to avoid shadowing other routes (405 error)
# MOVED: Global Options Handler (Catch-All) - REMOVED to avoid conflict with CORSMiddleware
# CORSMiddleware handles OPTIONS requests automatically.
