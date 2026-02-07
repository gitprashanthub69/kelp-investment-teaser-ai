from pydantic import BaseModel, EmailStr
from typing import List, Optional, Any, Dict
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    
    class Config:
        from_attributes = True

# Token
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Project Schemas
class ProjectBase(BaseModel):
    name: str
    company_name: str
    website: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class Artifact(BaseModel):
    id: int
    artifact_type: str
    created_at: datetime
    s3_key: Optional[str] = None
    version_id: Optional[str] = None

    class Config:
        from_attributes = True

class ArtifactResponse(BaseModel):
    id: int
    artifact_type: str
    created_at: datetime
    download_url: str 

class ProjectFile(BaseModel):
    id: int
    filename: str
    file_type: str
    
    class Config:
        from_attributes = True

class Project(ProjectBase):
    id: int
    status: str
    created_at: datetime
    sector: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    files: List[ProjectFile] = []
    artifacts: List[Artifact] = []
    
    class Config:
        from_attributes = True

class ProjectFileUpload(BaseModel):
    filename: str
    file_type: str
