from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import List
import logging
import uuid
from pathlib import Path

from .database import get_db, init_db
from . import models, schemas, services, tasks
from .config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.app_name)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path(__file__).parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化"""
    init_db()
    logger.info("数据库初始化完成")


@app.get("/health")
async def health_check():
    return {"status": "ok"}


# ========== AI 模型配置接口 ==========
@app.get("/api/ai-models/", response_model=List[schemas.AIModelConfigSchema])
async def list_ai_models(db: Session = Depends(get_db)):
    configs = await services.get_ai_model_configs(db)
    return configs


@app.post("/api/ai-models/", response_model=schemas.AIModelConfigSchema)
async def create_ai_model(config: schemas.AIModelConfigCreate, db: Session = Depends(get_db)):
    return await services.create_ai_model_config(db, config)


@app.get("/api/ai-models/{config_id}", response_model=schemas.AIModelConfigSchema)
async def get_ai_model(config_id: str, db: Session = Depends(get_db)):
    config = await services.get_ai_model_config(db, config_id)
    if not config:
        raise HTTPException(404, "配置不存在")
    return config


@app.put("/api/ai-models/{config_id}", response_model=schemas.AIModelConfigSchema)
async def update_ai_model(config_id: str, update: schemas.AIModelConfigUpdate, db: Session = Depends(get_db)):
    return await services.update_ai_model_config(db, config_id, update)


@app.delete("/api/ai-models/{config_id}")
async def delete_ai_model(config_id: str, db: Session = Depends(get_db)):
    await services.delete_ai_model_config(db, config_id)
    return {"message": "删除成功"}


@app.get("/api/ai-models/{config_id}/test")
async def test_ai_model(config_id: str, db: Session = Depends(get_db)):
    from .ai import ai_client
    config = await services.get_ai_model_config(db, config_id)
    if not config:
        raise HTTPException(404, "配置不存在")
    
    ai_client.load_config(config)
    result = ai_client.test_connection(config.model_type)
    return result


# ========== 岗位管理接口 ==========
@app.post("/api/jobs/", response_model=schemas.JobSchema)
async def create_job(job: schemas.JobCreate, db: Session = Depends(get_db)):
    return await services.create_job(db, job)


@app.get("/api/jobs/", response_model=List[schemas.JobSchema])
async def list_jobs(db: Session = Depends(get_db)):
    return await services.get_jobs(db)


@app.get("/api/jobs/{job_id}", response_model=schemas.JobDetailSchema)
async def get_job(job_id: str, db: Session = Depends(get_db)):
    job = await services.get_job_with_count(db, job_id)
    if not job:
        raise HTTPException(404, "岗位不存在")
    return job


@app.put("/api/jobs/{job_id}", response_model=schemas.JobSchema)
async def update_job(job_id: str, job: schemas.JobUpdate, db: Session = Depends(get_db)):
    return await services.update_job(db, job_id, job)


@app.delete("/api/jobs/{job_id}")
async def delete_job(job_id: str, db: Session = Depends(get_db)):
    await services.delete_job(db, job_id)
    return {"message": "删除成功"}


@app.post("/api/jobs/{job_id}/score-rules")
async def set_score_rules(job_id: str, rules: List[schemas.ScoreRule], db: Session = Depends(get_db)):
    return await services.update_score_rules(db, job_id, rules)


# ========== 简历上传接口 ==========
@app.post("/api/resumes/upload", response_model=schemas.UploadResponse)
async def upload_resumes(
    job_id: str = Form(...),
    files: List[UploadFile] = File(...)
):
    task_ids = []
    
    for file in files:
        file_ext = Path(file.filename).suffix.lower()
        file_path = UPLOAD_DIR / "resumes" / f"{uuid.uuid4()}{file_ext}"
        file_path.parent.mkdir(exist_ok=True)
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        db = next(get_db())
        try:
            resume = await services.create_resume(db, job_id, str(file_path), file_ext, len(content))
            task_ids.append(resume.id)
            
            tasks.task_queue.submit(tasks.process_resume, resume_id=resume.id)
        finally:
            db.close()
    
    return schemas.UploadResponse(task_ids=task_ids)


@app.get("/api/resumes/", response_model=List[schemas.ResumeSchema])
async def list_resumes(job_id: str, db: Session = Depends(get_db)):
    return await services.get_resumes(db, job_id)


@app.get("/api/resumes/{resume_id}", response_model=schemas.ResumeDetailSchema)
async def get_resume(resume_id: str, db: Session = Depends(get_db)):
    resume = await services.get_resume(db, resume_id)
    if not resume:
        raise HTTPException(404, "简历不存在")
    return resume


@app.get("/api/resumes/{resume_id}/status")
async def get_resume_status(resume_id: str, db: Session = Depends(get_db)):
    resume = await services.get_resume(db, resume_id)
    if not resume:
        raise HTTPException(404, "简历不存在")
    
    return {
        "id": resume.id,
        "status": resume.status,
        "progress": resume.status_progress,
        "message": resume.status_message,
        "error": resume.error_message
    }


# ========== 匹配结果接口 ==========
@app.get("/api/matching/results/{job_id}")
async def get_matching_results(job_id: str, min_score: float = 0, db: Session = Depends(get_db)):
    return await services.get_matching_results(db, job_id, min_score)


@app.get("/api/matching/results/{resume_id}/detail")
async def get_matching_detail(resume_id: str, db: Session = Depends(get_db)):
    result = await services.get_matching_result(db, resume_id)
    if not result:
        raise HTTPException(404, "未找到匹配结果")
    return result


@app.get("/api/matching/results/{resume_id}/report")
async def get_analysis_report(resume_id: str, db: Session = Depends(get_db)):
    report = await services.get_analysis_report(db, resume_id)
    if not report:
        raise HTTPException(404, "未找到报告")
    return PlainTextResponse(report)


# ========== 面试题目接口 ==========
@app.get("/api/interviews/questions/{resume_id}")
async def get_interview_questions(resume_id: str, db: Session = Depends(get_db)):
    return await services.get_interview_questions(db, resume_id)


@app.get("/api/interviews/questions/{resume_id}/export")
async def export_questions(resume_id: str, format: str = "txt", db: Session = Depends(get_db)):
    content = await services.export_questions(db, resume_id, format)
    return PlainTextResponse(content)


# ========== 人才库接口 ==========
@app.get("/api/talent-pool/")
async def list_talent_pool(
    keyword: str = None,
    skills: str = None,
    min_experience: int = None,
    education: str = None,
    status: str = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    return await services.search_talent_pool(
        db, keyword, skills, min_experience, education, status, page, page_size
    )


@app.get("/api/talent-pool/{talent_id}")
async def get_talent_detail(talent_id: str, db: Session = Depends(get_db)):
    talent = await services.get_talent(db, talent_id)
    if not talent:
        raise HTTPException(404, "人才不存在")
    return talent


@app.post("/api/talent-pool/{talent_id}/tags")
async def add_talent_tags(talent_id: str, data: schemas.AddTalentTags, db: Session = Depends(get_db)):
    return await services.add_talent_tags(db, talent_id, data.tags)


@app.post("/api/talent-pool/{talent_id}/notes")
async def update_talent_notes(talent_id: str, data: schemas.UpdateTalentNotes, db: Session = Depends(get_db)):
    return await services.update_talent_notes(db, talent_id, data.notes)


@app.post("/api/talent-pool/resumes/{resume_id}/add")
async def add_resume_to_talent_pool(resume_id: str, db: Session = Depends(get_db)):
    resume = await services.get_resume(db, resume_id)
    if not resume:
        raise HTTPException(404, "简历不存在")
    
    job = await services.get_job(db, resume.job_id)
    talent = await services.add_to_talent_pool(db, resume_id, job)
    return talent


# ========== 异常处理 ==========
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"全局异常：{exc}")
    return JSONResponse(
        status_code=500,
        content={"error": True, "message": "服务器内部错误"}
    )
