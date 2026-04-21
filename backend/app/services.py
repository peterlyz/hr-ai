from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional, Dict, Any
from . import models, schemas
from .ai import ai_client
from .parser import MarkItDownParser
from datetime import datetime
import json


# ========== AI 模型配置服务 ==========
async def get_ai_model_configs(db: Session) -> List[models.AIModelConfig]:
    return db.query(models.AIModelConfig).all()


async def get_ai_model_config(db: Session, config_id: str) -> Optional[models.AIModelConfig]:
    return db.query(models.AIModelConfig).filter(models.AIModelConfig.id == config_id).first()


async def create_ai_model_config(db: Session, config: schemas.AIModelConfigCreate) -> models.AIModelConfig:
    db_config = models.AIModelConfig(**config.model_dump())
    if config.is_default:
        db.query(models.AIModelConfig).filter(
            models.AIModelConfig.model_type == config.model_type
        ).update({"is_default": False})
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config


async def update_ai_model_config(db: Session, config_id: str, update: schemas.AIModelConfigUpdate) -> models.AIModelConfig:
    db_config = db.query(models.AIModelConfig).filter(models.AIModelConfig.id == config_id).first()
    if not db_config:
        raise ValueError("配置不存在")
    
    update_data = update.model_dump(exclude_unset=True)
    if update.is_default and update_data.get("is_default"):
        db.query(models.AIModelConfig).filter(
            models.AIModelConfig.model_type == db_config.model_type,
            models.AIModelConfig.id != config_id
        ).update({"is_default": False})
    
    for key, value in update_data.items():
        setattr(db_config, key, value)
    
    db.commit()
    db.refresh(db_config)
    return db_config


async def delete_ai_model_config(db: Session, config_id: str):
    db_config = db.query(models.AIModelConfig).filter(models.AIModelConfig.id == config_id).first()
    if db_config:
        db.delete(db_config)
        db.commit()


async def get_default_ai_configs(db: Session) -> Dict[str, models.AIModelConfig]:
    """获取默认模型配置"""
    llm = db.query(models.AIModelConfig).filter(
        models.AIModelConfig.model_type == "llm",
        models.AIModelConfig.is_default == True
    ).first()
    embedding = db.query(models.AIModelConfig).filter(
        models.AIModelConfig.model_type == "embedding",
        models.AIModelConfig.is_default == True
    ).first()
    
    return {"llm": llm, "embedding": embedding}


# ========== 岗位管理服务 ==========
async def create_job(db: Session, job: schemas.JobCreate) -> models.JobPosting:
    db_job = models.JobPosting(**job.model_dump())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


async def get_jobs(db: Session) -> List[models.JobPosting]:
    return db.query(models.JobPosting).order_by(models.JobPosting.created_at.desc()).all()


async def get_job(db: Session, job_id: str) -> Optional[models.JobPosting]:
    return db.query(models.JobPosting).filter(models.JobPosting.id == job_id).first()


async def update_job(db: Session, job_id: str, job: schemas.JobUpdate) -> models.JobPosting:
    db_job = db.query(models.JobPosting).filter(models.JobPosting.id == job_id).first()
    if not db_job:
        raise ValueError("岗位不存在")
    
    update_data = job.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_job, key, value)
    
    db.commit()
    db.refresh(db_job)
    return db_job


async def delete_job(db: Session, job_id: str):
    db_job = db.query(models.JobPosting).filter(models.JobPosting.id == job_id).first()
    if db_job:
        db.delete(db_job)
        db.commit()


async def update_score_rules(db: Session, job_id: str, rules: List[schemas.ScoreRule]) -> models.JobPosting:
    db_job = db.query(models.JobPosting).filter(models.JobPosting.id == job_id).first()
    if not db_job:
        raise ValueError("岗位不存在")
    
    db_job.score_rules = [rule.model_dump() for rule in rules]
    db.commit()
    db.refresh(db_job)
    return db_job


async def get_job_with_count(db: Session, job_id: str) -> Dict[str, Any]:
    job = await get_job(db, job_id)
    if not job:
        return None
    
    resume_count = db.query(models.Resume).filter(models.Resume.job_id == job_id).count()
    return {**schemas.JobSchema.model_validate(job).model_dump(), "resume_count": resume_count}


# ========== 简历管理服务 ==========
async def create_resume(db: Session, job_id: str, file_path: str, file_type: str, file_size: int) -> models.Resume:
    db_resume = models.Resume(
        job_id=job_id,
        file_path=file_path,
        file_type=file_type,
        file_size=file_size,
        status="uploading",
        status_progress=0
    )
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)
    return db_resume


async def get_resumes(db: Session, job_id: Optional[str] = None) -> List[models.Resume]:
    query = db.query(models.Resume)
    if job_id:
        query = query.filter(models.Resume.job_id == job_id)
    return query.order_by(models.Resume.created_at.desc()).all()


async def get_resume(db: Session, resume_id: str) -> Optional[models.Resume]:
    return db.query(models.Resume).filter(models.Resume.id == resume_id).first()


async def update_resume_status(
    db: Session, 
    resume_id: str, 
    status: str, 
    progress: int = None,
    message: str = None,
    parsed_content: Dict = None
):
    db_resume = db.query(models.Resume).filter(models.Resume.id == resume_id).first()
    if not db_resume:
        raise ValueError("简历不存在")
    
    db_resume.status = status
    if progress is not None:
        db_resume.status_progress = progress
    if message:
        db_resume.status_message = message
    if parsed_content:
        db_resume.parsed_content = parsed_content
    
    db.commit()
    db.refresh(db_resume)
    return db_resume


# ========== 匹配结果服务 ==========
async def save_matching_result(db: Session, resume_id: str, result: Dict):
    db_result = models.MatchingResult(
        resume_id=resume_id,
        total_score=result["total_score"],
        recommendation=result["recommendation"],
        summary=result["summary"],
        analysis_report=result["analysis_report"],
        dimension_scores=[ds.model_dump() if hasattr(ds, 'model_dump') else ds for ds in result["dimension_scores"]]
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result


async def get_matching_result(db: Session, resume_id: str) -> Optional[models.MatchingResult]:
    return db.query(models.MatchingResult).filter(models.MatchingResult.resume_id == resume_id).first()


async def get_matching_results(db: Session, job_id: str, min_score: float = 0) -> List[Dict]:
    results = db.query(models.MatchingResult).join(models.Resume).filter(
        models.Resume.job_id == job_id,
        models.MatchingResult.total_score >= min_score
    ).order_by(models.MatchingResult.total_score.desc()).all()
    
    return [schemas.MatchingResultSchema.model_validate(r).model_dump() for r in results]


async def get_analysis_report(db: Session, resume_id: str) -> Optional[str]:
    result = await get_matching_result(db, resume_id)
    return result.analysis_report if result else None


# ========== 面试题目服务 ==========
async def save_interview_questions(db: Session, resume_id: str, questions: List[Dict]):
    for i, q in enumerate(questions):
        db_question = models.InterviewQuestion(
            resume_id=resume_id,
            question=q["question"],
            answer=q["answer"],
            category=q["category"],
            difficulty=q["difficulty"],
            sort_order=i
        )
        db.add(db_question)
    db.commit()


async def get_interview_questions(db: Session, resume_id: str) -> List[models.InterviewQuestion]:
    return db.query(models.InterviewQuestion).filter(
        models.InterviewQuestion.resume_id == resume_id
    ).order_by(models.InterviewQuestion.sort_order).all()


async def export_questions(db: Session, resume_id: str, format: str = "txt") -> str:
    questions = await get_interview_questions(db, resume_id)
    if not questions:
        raise ValueError("未找到面试题目")
    
    if format == "txt":
        content = f"面试题目（共{len(questions)}道）\n\n"
        for i, q in enumerate(questions, 1):
            content += f"{i}. [{q.category}] {q.question}\n"
            content += f"   参考答案：{q.answer}\n\n"
    else:
        content = json.dumps([schemas.InterviewQuestionSchema.model_validate(q).model_dump() for q in questions], ensure_ascii=False, indent=2)
    
    return content


# ========== 人才库服务 ==========
async def add_to_talent_pool(db: Session, resume_id: str, job: models.JobPosting = None):
    resume = db.query(models.Resume).filter(models.Resume.id == resume_id).first()
    if not resume:
        raise ValueError("简历不存在")
    
    # 检查是否已在人才库
    existing = db.query(models.TalentPool).filter(models.TalentPool.resume_id == resume_id).first()
    if existing:
        return existing
    
    matching_result = db.query(models.MatchingResult).filter(models.MatchingResult.resume_id == resume_id).first()
    if not matching_result or matching_result.total_score < 60:
        raise ValueError("简历匹配分低于 60，不建议加入人才库")
    
    # 提取简历信息
    parsed = resume.parsed_content or {}
    raw_text = parsed.get("raw_text", "")
    
    # 使用 AI 提取关键信息
    ai_client_instance = ai_client
    try:
        extraction_prompt = f"""
请从以下简历文本中提取关键信息，返回 JSON 格式：
{{
    "candidate_name": "姓名",
    "phone": "电话",
    "email": "邮箱",
    "current_company": "当前公司",
    "current_position": "当前职位",
    "years_of_experience": 工作年限（数字）,
    "highest_education": "最高学历",
    "major": "专业",
    "skills": ["技能 1", "技能 2"]
}}

简历内容：
{raw_text[:3000]}
"""
        # 简化处理，先不提取详细信息
        talent = models.TalentPool(
            resume_id=resume_id,
            candidate_name=resume.candidate_name,
            skills=[],
            job_history=[],
            best_score=matching_result.total_score,
            best_match_job=job.title if job else None,
            embedding=ai_client_instance.embed([raw_text[:2000]]) if ai_client_instance._get_embedding_config() else None
        )
        db.add(talent)
        db.commit()
        db.refresh(talent)
        return talent
    except Exception as e:
        raise ValueError(f"提取简历信息失败：{str(e)}")


async def search_talent_pool(
    db: Session,
    keyword: str = None,
    skills: str = None,
    min_experience: int = None,
    education: str = None,
    status: str = None,
    page: int = 1,
    page_size: int = 20
):
    query = db.query(models.TalentPool)
    
    if keyword:
        query = query.filter(or_(
            models.TalentPool.candidate_name.like(f"%{keyword}%"),
            models.TalentPool.current_company.like(f"%{keyword}%"),
            models.TalentPool.current_position.like(f"%{keyword}%"),
            models.TalentPool.major.like(f"%{keyword}%")
        ))
    
    if skills:
        skill_list = skills.split(",")
        for skill in skill_list:
            query = query.filter(models.TalentPool.skills.contains([skill.strip()]))
    
    if min_experience is not None:
        query = query.filter(models.TalentPool.years_of_experience >= min_experience)
    
    if education:
        query = query.filter(models.TalentPool.highest_education == education)
    
    if status:
        query = query.filter(models.TalentPool.status == status)
    
    total = query.count()
    talents = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "data": [schemas.TalentPoolSchema.model_validate(t).model_dump() for t in talents]
    }


async def get_talent(db: Session, talent_id: str) -> Optional[models.TalentPool]:
    return db.query(models.TalentPool).filter(models.TalentPool.id == talent_id).first()


async def add_talent_tags(db: Session, talent_id: str, tags: List[str]):
    talent = await get_talent(db, talent_id)
    if not talent:
        raise ValueError("人才不存在")
    
    current_tags = talent.tags or []
    new_tags = list(set(current_tags + tags))
    talent.tags = new_tags
    db.commit()
    db.refresh(talent)
    return talent


async def update_talent_notes(db: Session, talent_id: str, notes: str):
    talent = await get_talent(db, talent_id)
    if not talent:
        raise ValueError("人才不存在")
    
    talent.notes = notes
    db.commit()
    db.refresh(talent)
    return talent


async def search_similar_talents(db: Session, resume_id: str, limit: int = 10):
    """基于向量相似度搜索人才（简化版，暂不实现）"""
    # TODO: 实现向量相似度搜索
    return []
