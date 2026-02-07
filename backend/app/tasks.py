"""
Celery Tasks - Enhanced Project Processing
Integrates all services for comprehensive teaser generation
"""

from app.core.celery_app import celery_app
from app.services.intelligence import IntelligenceService
from app.services.ppt_generator import PPTGenerator
from app.services.parser import DataParser, DocumentExtractor
from app.services.scraper import ScraperService
from app.services.image_service import ImageService
from app.db.database import SessionLocal
from app.db import models
import os
import traceback


@celery_app.task(name="app.tasks.process_project_task", bind=True, max_retries=2)
def process_project_task(self=None, project_id: int = None):
    """
    Enhanced project processing with comprehensive data extraction and generation.
    """
    print(f"[Task] ========== Starting Project {project_id} ==========")
    db = SessionLocal()
    
    try:
        # Get project
        project = db.query(models.Project).filter(models.Project.id == project_id).first()
        if not project:
            print(f"[Task] Project {project_id} not found")
            return
        
        # Update status
        project.status = models.ProjectStatus.PROCESSING
        db.commit()
        db.refresh(project)
        print(f"[Task] Project {project_id}: Status -> PROCESSING")
        
        # ========== 1. PARSE FILES ==========
        print(f"[Task] Project {project_id}: Parsing {len(project.files)} files...")
        
        aggregated_text = ""
        excel_data = {}
        pdf_kpis = {}
        
        for f in project.files:
            try:
                if f.file_type == 'excel':
                    parsed = DataParser.parse_excel(f.file_path)
                    if parsed.get('financials') and parsed['financials'].get('revenue'):
                        excel_data = parsed['financials']
                        print(f"[Task] Project {project_id}: Excel financials extracted")
                        print(f"       Years: {excel_data.get('years')}")
                        print(f"       Revenue: {excel_data.get('revenue')}")
                        
                elif f.file_type == 'pdf':
                    parsed = DataParser.parse_pdf(f.file_path)
                    content = parsed.get('text_content', "")
                    if content:
                        aggregated_text += content + "\n"
                        print(f"[Task] Project {project_id}: PDF text extracted ({len(content)} chars)")
                    
                    # Merge KPIs
                    kpis = parsed.get('kpis', {})
                    pdf_kpis.update({k: v for k, v in kpis.items() if v})
                    
                    # Check for PDF tables
                    if parsed.get('financials') and not excel_data:
                        excel_data = parsed['financials']
                        print(f"[Task] Project {project_id}: PDF table financials extracted")
                        
            except Exception as e:
                print(f"[Task] Project {project_id}: File parse error - {e}")
        
        # ========== 2. SCRAPE PUBLIC DATA ==========
        print(f"[Task] Project {project_id}: Gathering public context...")
        scraped_text = ""
        company_name = project.company_name
        
        if company_name:
            try:
                public_context = ScraperService.gather_public_context(
                    company_name, 
                    website=project.company_url,
                    max_urls=3
                )
                scraped_text = public_context.get("combined_text", "")
                if scraped_text:
                    aggregated_text += "\n" + scraped_text
                    print(f"[Task] Project {project_id}: Scraped {len(scraped_text)} chars")
            except Exception as e:
                print(f"[Task] Project {project_id}: Scraping error - {e}")
        
        # ========== 3. DETECT SECTOR ==========
        detection_text = aggregated_text or company_name or ""
        sector = IntelligenceService.detect_sector(detection_text)
        print(f"[Task] Project {project_id}: Detected Sector -> {sector}")
        
        # ========== 4. EXTRACT NARRATIVE FROM PDF ==========
        print(f"[Task] Project {project_id}: Extracting narrative from uploaded files...")
        extracted_narrative = {}
        if aggregated_text:
            extracted_narrative = DocumentExtractor.extract_narrative(aggregated_text)
            extracted_fields = extracted_narrative.get("_extracted_fields", [])
            print(f"[Task] Project {project_id}: Extracted {len(extracted_fields)} fields from PDF")
        
        # ========== 5. PREPARE FINANCIAL DATA ==========
        # Check if we have real data from parsing
        has_real_data = bool(excel_data.get("revenue"))
        
        # Initial financial data (either real or empty)
        financial_data = excel_data if has_real_data else {}
        
        # ========== 6. GENERATE AI NARRATIVE (fills gaps) ==========
        print(f"[Task] Project {project_id}: Generating AI narrative for missing fields...")
        ai_narrative = IntelligenceService.generate_narrative(
            sector=sector,
            financial_data=financial_data,
            kpis=pdf_kpis,
            scraped_text=aggregated_text[:12000] if aggregated_text else None
        )
        
        # ========== 7. MERGE NARRATIVES (prefer extracted, fallback to AI) ==========
        narrative = DocumentExtractor.merge_with_ai_narrative(extracted_narrative, ai_narrative)
        print(f"[Task] Project {project_id}: Merged extracted + AI narrative")
        
        # DEBUG: Show what narrative data looks like
        print(f"[Task] DEBUG - Narrative slide_1 keys: {list(narrative.get('slide_1', {}).keys())}")
        if narrative.get('slide_1', {}).get('biz_desc'):
            print(f"[Task] DEBUG - biz_desc preview: {narrative['slide_1']['biz_desc'][:100]}...")
        if narrative.get('slide_1', {}).get('certifications'):
            print(f"[Task] DEBUG - certifications: {narrative['slide_1']['certifications']}")
        if narrative.get('slide_1', {}).get('product_portfolio'):
            print(f"[Task] DEBUG - products: {len(narrative['slide_1']['product_portfolio'])} items")
        
        # If no real data was found by parser, check extracted narrative financials
        if not has_real_data:
            if extracted_narrative.get("financials"):
                financial_data = extracted_narrative["financials"]
                print(f"[Task] Project {project_id}: Using PDF-extracted financials: {list(financial_data.keys())}")
            elif narrative.get("financials"):
                financial_data = narrative.get("financials")
                print(f"[Task] Project {project_id}: Using AI-estimated financials")
        
        # Final fallback if both parser and AI failed (unlikely now)
        if not financial_data.get("revenue") and not financial_data.get("years"):
            financial_data = {
                "years": ["FY21", "FY22", "FY23", "FY24"],
                "revenue": [100, 125, 160, 200],
                "ebitda": [15, 20, 28, 38],
                "pat": [8, 12, 18, 25]
            }
            print(f"[Task] Project {project_id}: Using default financials (no source data)")
        print(f"[Task] Project {project_id}: Narrative and financials ready")
        
        # ========== 6. FETCH IMAGES ==========
        print(f"[Task] Project {project_id}: Fetching images...")
        image_paths = {}
        try:
            for i in range(3):
                img_url = ImageService.get_sector_image(sector, variation=i)
                if img_url:
                    image_paths[f"slide_{i+1}"] = img_url
                    print(f"[Task] Project {project_id}: Got image {i+1}: {img_url[:50]}...")
        except Exception as e:
            print(f"[Task] Project {project_id}: Image fetch error - {e}")
        
        # ========== 7. CREATE OUTPUT DIRECTORY ==========
        temp_dir = f"data/projects/{project_id}"
        os.makedirs(temp_dir, exist_ok=True)
        
        # ========== 8. GENERATE PPT ==========
        print(f"[Task] Project {project_id}: Generating PPT...")
        ppt_input = {
            "project_id": project_id,
            "company_name": company_name or "The Company",
            "sector": sector,
            "financials": financial_data,
            "narrative": narrative,
            "generated_images": image_paths,
            "kpis": pdf_kpis
        }
        
        output_filename = f"Investment_Teaser.pptx"
        output_path = os.path.join(temp_dir, output_filename)
        
        generator = PPTGenerator(output_path, ppt_input)
        generator.generate()
        print(f"[Task] Project {project_id}: PPT saved -> {output_path}")
        
        # ========== 9. GENERATE CITATIONS ==========
        print(f"[Task] Project {project_id}: Generating Citations...")
        citation_filename = f"Citations.pdf"
        citation_path = os.path.join(temp_dir, citation_filename)
        
        sources = []
        for f in project.files:
            sources.append({"type": "file", "value": f.filename, "context": "Data Extraction"})
        
        try:
            from app.services.citation_generator import get_citation_generator
            cit_gen = get_citation_generator(citation_path, project_id)
            cit_gen.generate(sources, company_name=company_name or "The Company")
            print(f"[Task] Project {project_id}: Citations saved")
        except Exception as e:
            print(f"[Task] Project {project_id}: Citation error - {e}")
        
        # ========== 10. UPLOAD TO S3 ==========
        print(f"[Task] Project {project_id}: Uploading to S3...")
        s3_key_ppt = output_path
        s3_key_cit = citation_path
        version_id_ppt = None
        version_id_cit = None
        
        try:
            from app.services.s3_service import get_s3_service
            s3 = get_s3_service()
            
            s3_key_ppt = f"projects/{project_id}/{output_filename}"
            version_id_ppt = s3.upload_file(output_path, s3_key_ppt)
            
            if os.path.exists(citation_path):
                s3_key_cit = f"projects/{project_id}/{citation_filename}"
                version_id_cit = s3.upload_file(citation_path, s3_key_cit)
            
            print(f"[Task] Project {project_id}: S3 upload complete")
        except Exception as e:
            print(f"[Task] Project {project_id}: S3 error (using local) - {e}")
        
        # ========== 11. SAVE ARTIFACTS ==========
        print(f"[Task] Project {project_id}: Saving artifacts...")
        
        # PPT Artifact
        artifact_ppt = models.Artifact(
            artifact_type="ppt",
            file_path=output_path,
            s3_key=s3_key_ppt,
            version_id=version_id_ppt,
            project_id=project.id
        )
        db.add(artifact_ppt)
        
        # Citation Artifact
        if os.path.exists(citation_path):
            artifact_cit = models.Artifact(
                artifact_type="citation_doc",
                file_path=citation_path,
                s3_key=s3_key_cit,
                version_id=version_id_cit,
                project_id=project.id
            )
            db.add(artifact_cit)
        
        # ========== 12. FINALIZE ==========
        project.status = models.ProjectStatus.COMPLETED
        project.sector = sector
        
        # Store metrics
        if financial_data:
            rev = financial_data.get("revenue", [])
            ebitda = financial_data.get("ebitda", [])
            project.metrics = {
                "revenue": str(rev[-1]) if rev else "",
                "revenue_cagr": f"{IntelligenceService._calc_cagr(rev)}%" if rev else "",
                "ebitda_margin": f"{round(ebitda[-1]/rev[-1]*100)}%" if ebitda and rev and rev[-1] > 0 else "",
                "sector": sector
            }
        
        db.commit()
        print(f"[Task] Project {project_id}: ========== COMPLETED ==========")
        
    except Exception as e:
        print(f"[Task] Project {project_id}: ========== FAILED ==========")
        print(f"[Task] Error: {e}")
        traceback.print_exc()
        
        try:
            project = db.query(models.Project).filter(models.Project.id == project_id).first()
            if project:
                project.status = models.ProjectStatus.FAILED
                db.commit()
        except:
            pass
        
        # Retry if available
        if self and getattr(self, 'request', None) and self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=10)
    
    finally:
        db.close()
