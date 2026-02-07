from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.api import deps
from app.db import models
from app.schemas import Project, ProjectCreate
from app.services import project_service, generator_service
from app.services.parser import DataParser
from fastapi import BackgroundTasks
from fastapi.responses import FileResponse
import os
import shutil

router = APIRouter()

@router.post("/", response_model=Project)
def create_project(
    project_in: ProjectCreate,
    current_user: models.User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    return project_service.create_project(db=db, project_in=project_in, user_id=current_user.id)

@router.get("/", response_model=List[Project])
def read_projects(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    projects = project_service.get_projects(db, user_id=current_user.id, skip=skip, limit=limit)
    return projects

@router.get("/{project_id}", response_model=Project)
def read_project(
    project_id: int,
    current_user: models.User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    project = project_service.get_project(db, project_id=project_id, user_id=current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    current_user: models.User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    success = project_service.delete_project(db, project_id=project_id, user_id=current_user.id)
    if not success:
         raise HTTPException(status_code=404, detail="Project not found")
    return {"status": "success"}

@router.post("/{project_id}/upload")
async def upload_project_file(
    project_id: int,
    file: UploadFile = File(...),
    current_user: models.User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    # Verify ownership
    project = project_service.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # UPLOAD_DIR relative to backend/
    project_dir = f"data/projects/{project_id}"
    os.makedirs(project_dir, exist_ok=True)
    
    file_location = f"{project_dir}/{file.filename}"
    
    # Save file
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Determine type and parse
    parsed_data = {}
    file_type = "unknown"
    if file.filename.endswith('.xlsx'):
        file_type = "excel"
        parsed_data = DataParser.parse_excel(file_location)
    elif file.filename.endswith('.pdf'):
        file_type = "pdf"
        parsed_data = DataParser.parse_pdf(file_location)
        
    # Save metadata
    db_file = models.ProjectFile(
        filename=file.filename,
        file_path=file_location,
        file_type=file_type,
        parsed_data=parsed_data,
        project_id=project.id
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    
    return {
        "id": db_file.id,
        "filename": db_file.filename,
        "parsed_preview": parsed_data
    }

@router.post("/{project_id}/generate")
def generate_project(
    project_id: int,
    background_tasks: BackgroundTasks,
    current_user: models.User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    project = project_service.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    background_tasks.add_task(generator_service.GeneratorService.process_project, project_id)
    return {"status": "queued", "project_id": project_id}

@router.get("/{project_id}/download/{artifact_type}")
def download_artifact(
    project_id: int,
    artifact_type: str,
    current_user: models.User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    # Verify ownership
    project = project_service.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    # Find artifact
    artifact = db.query(models.Artifact).filter(
        models.Artifact.project_id == project_id,
        models.Artifact.artifact_type == artifact_type
    ).order_by(models.Artifact.created_at.desc()).first()
    
    if not artifact or not os.path.exists(artifact.file_path):
        raise HTTPException(status_code=404, detail="Artifact not found")
        
    filename = os.path.basename(artifact.file_path)
    ext = os.path.splitext(filename)[1].lower()
    if ext == ".pdf":
        media_type = "application/pdf"
    else:
        media_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    return FileResponse(artifact.file_path, filename=filename, media_type=media_type)
