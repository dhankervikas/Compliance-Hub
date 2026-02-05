import logging
from app.database import engine, Base
from app.models.audit_assessment import AuditAssessment

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_table():
    logger.info("Creating audit_assessments table...")
    try:
        AuditAssessment.__table__.create(bind=engine)
        logger.info("Table 'audit_assessments' created successfully.")
    except Exception as e:
        logger.error(f"Error creating table: {e}")

if __name__ == "__main__":
    create_table()
