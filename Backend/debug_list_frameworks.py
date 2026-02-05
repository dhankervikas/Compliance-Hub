
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.framework import Framework
from app.models.control import Control

def list_frameworks():
    db = SessionLocal()
    with open("frameworks_dump.txt", "w") as f_out:
        f_out.write("Listing All Frameworks and Control Counts:\n")
        fws = db.query(Framework).all()
        for f in fws:
            count = db.query(Control).filter(Control.framework_id == f.id).count()
            f_out.write(f"ID: {f.id} | Code: {f.code} | Name: {f.name} | Controls: {count}\n")
    db.close()
    print("Done. Wrote to frameworks_dump.txt")

if __name__ == "__main__":
    list_frameworks()
