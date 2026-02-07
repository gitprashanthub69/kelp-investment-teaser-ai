import os
import uuid
import time
import re
from sqlalchemy.orm import Session
from app.db import models
from app.services.intelligence import IntelligenceService
from app.services.ppt_generator import PPTGenerator
from app.services.parser import DataParser
from app.services.scraper import ScraperService
from app.services.openai_service import get_openai_service, OpenAIService

from app.db.database import SessionLocal

from app.tasks import process_project_task

class GeneratorService:
    @staticmethod
    def process_project(project_id: int):
        """Execute the project processing task directly (bypassing Celery for local dev)"""
        print(f"Executing task directly for Project {project_id}")
        try:
            # We call the function directly. Since this is likely called 
            # within a FastAPI BackgroundTask, it will still run off the main thread.
            process_project_task(project_id)
            return {"message": "Processing complete", "project_id": project_id}
        except Exception as e:
            print(f"Error in direct task execution: {e}")
            return {"message": f"Error: {e}", "project_id": project_id}

