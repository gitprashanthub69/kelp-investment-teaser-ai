from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, DateTime, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import enum

class ProjectStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    
    projects = relationship("Project", back_populates="owner")

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True) # Internal project name
    company_name = Column(String) # Target company
    website = Column(String, nullable=True)
    sector = Column(String, nullable=True)
    metrics = Column(JSON, nullable=True) # Summary metrics for dashboard card
    
    status = Column(String, default=ProjectStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="projects")
    
    files = relationship("ProjectFile", back_populates="project")
    artifacts = relationship("Artifact", back_populates="project")

class ProjectFile(Base):
    __tablename__ = "project_files"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    file_path = Column(String)
    file_type = Column(String) # pdf, excel
    parsed_data = Column(JSON, nullable=True)
    s3_key = Column(String, nullable=True)
    version_id = Column(String, nullable=True)
    
    project_id = Column(Integer, ForeignKey("projects.id"))
    project = relationship("Project", back_populates="files")

class Artifact(Base):
    __tablename__ = "artifacts"
    
    id = Column(Integer, primary_key=True, index=True)
    artifact_type = Column(String) # ppt, citation_doc
    file_path = Column(String)
    s3_key = Column(String, nullable=True)
    version_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    project_id = Column(Integer, ForeignKey("projects.id"))
    project = relationship("Project", back_populates="artifacts")
