from sqlalchemy import Column, String, Integer, Float, Text, ForeignKey, DateTime, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .database import Base


def generate_uuid():
    return str(uuid.uuid4())


class JobPosting(Base):
    """岗位"""
    __tablename__ = "job_postings"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String(200), nullable=False)
    department = Column(String(100))
    jd_content = Column(Text, nullable=False)
    jd_file_path = Column(String(500))
    status = Column(String(20), default='active')
    score_rules = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    resumes = relationship("Resume", back_populates="job", cascade="all, delete-orphan")


class Resume(Base):
    """简历"""
    __tablename__ = "resumes"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    job_id = Column(String, ForeignKey('job_postings.id'), nullable=False)
    candidate_name = Column(String(100))
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(20))
    file_size = Column(Integer)
    parsed_content = Column(JSON)
    status = Column(String(50), default='uploading')
    status_progress = Column(Integer, default=0)
    status_message = Column(Text)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    job = relationship("JobPosting", back_populates="resumes")
    matching_result = relationship("MatchingResult", back_populates="resume", uselist=False, cascade="all, delete-orphan")
    interview_questions = relationship("InterviewQuestion", back_populates="resume", cascade="all, delete-orphan")


class MatchingResult(Base):
    """匹配结果"""
    __tablename__ = "matching_results"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    resume_id = Column(String, ForeignKey('resumes.id'), unique=True, nullable=False)
    total_score = Column(Float, nullable=False)
    recommendation = Column(String(50))
    summary = Column(Text)
    analysis_report = Column(Text)
    dimension_scores = Column(JSON)
    created_at = Column(DateTime, default=datetime.now)
    
    resume = relationship("Resume", back_populates="matching_result")


class InterviewQuestion(Base):
    """面试题目"""
    __tablename__ = "interview_questions"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    resume_id = Column(String, ForeignKey('resumes.id'), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    category = Column(String(50))
    difficulty = Column(String(20))
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    
    resume = relationship("Resume", back_populates="interview_questions")


class AIModelConfig(Base):
    """AI 模型配置"""
    __tablename__ = "ai_model_configs"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False, unique=True)
    model_type = Column(String(20), nullable=False)
    provider = Column(String(50), nullable=False)
    base_url = Column(String(500))
    api_key = Column(String(500))
    model_name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    extra_config = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class TalentPool(Base):
    """人才库"""
    __tablename__ = "talent_pool"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    resume_id = Column(String, ForeignKey('resumes.id'), unique=True, nullable=False)
    candidate_name = Column(String(100))
    phone = Column(String(50))
    email = Column(String(200))
    current_company = Column(String(200))
    current_position = Column(String(200))
    years_of_experience = Column(Integer)
    highest_education = Column(String(100))
    major = Column(String(200))
    skills = Column(JSON)
    job_history = Column(JSON)
    best_score = Column(Float)
    best_match_job = Column(String(200))
    status = Column(String(50), default='active')
    tags = Column(JSON, default=list)
    notes = Column(Text)
    embedding = Column(JSON)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    resume = relationship("Resume", backref="talent_profile", uselist=False)


class TalentInteraction(Base):
    """人才互动记录"""
    __tablename__ = "talent_interactions"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    talent_id = Column(String, ForeignKey('talent_pool.id'), nullable=False)
    interaction_type = Column(String(50))
    job_id = Column(String, ForeignKey('job_postings.id'))
    result = Column(String(100))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    
    talent = relationship("TalentPool", backref="interactions")
    job = relationship("JobPosting")
