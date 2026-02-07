from sqlalchemy.orm import Session, joinedload
from app.db import models
from app.schemas import ProjectCreate

def create_project(db: Session, project_in: ProjectCreate, user_id: int):
    db_project = models.Project(
        **project_in.dict(),
        owner_id=user_id,
        status=models.ProjectStatus.PENDING
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def get_projects(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Project)\
        .options(joinedload(models.Project.files), joinedload(models.Project.artifacts))\
        .filter(models.Project.owner_id == user_id)\
        .offset(skip).limit(limit).all()

def get_project(db: Session, project_id: int, user_id: int):
    return db.query(models.Project)\
        .options(joinedload(models.Project.files), joinedload(models.Project.artifacts))\
        .filter(models.Project.id == project_id, models.Project.owner_id == user_id)\
        .first()

def delete_project(db: Session, project_id: int, user_id: int):
    project = get_project(db, project_id, user_id)
    if project:
        db.delete(project)
        db.commit()
    return project
