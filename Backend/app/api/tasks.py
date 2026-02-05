from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import json
import os
from datetime import datetime

router = APIRouter()

TASKS_FILE = "tasks.json"

class TaskCreate(BaseModel):
    title: str
    description: str
    document_id: Optional[str] = None
    control_id: Optional[str] = None
    assigned_to: str = "Admin"

class Task(TaskCreate):
    id: str
    status: str # "PENDING", "APPROVED", "REJECTED"
    created_at: str

def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    try:
        with open(TASKS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_tasks(tasks):
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=2)

@router.get("/", response_model=List[Task])
def get_tasks():
    return load_tasks()

@router.post("/request-approval", response_model=Task)
def request_approval(task_in: TaskCreate):
    tasks = load_tasks()
    
    new_task = {
        "id": f"TASK-{len(tasks) + 1001}",
        "title": task_in.title,
        "description": task_in.description,
        "document_id": task_in.document_id,
        "control_id": task_in.control_id,
        "assigned_to": task_in.assigned_to,
        "status": "PENDING",
        "created_at": datetime.now().isoformat()
    }
    
    tasks.append(new_task)
    save_tasks(tasks)
    return new_task

@router.post("/{task_id}/approve")
def approve_task(task_id: str):
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == task_id:
            t["status"] = "APPROVED"
            t["completed_at"] = datetime.now().isoformat()
            save_tasks(tasks)
            return {"status": "success", "message": f"Task {task_id} approved"}
    
    raise HTTPException(status_code=404, detail="Task not found")
