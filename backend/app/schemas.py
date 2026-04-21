from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ModelType(str, Enum):
    LLM = "llm"
    EMBEDDING = "embedding"


class ModelProvider(str, Enum):
    DASHSCOPE = "dashscope"
    OPENAI = "openai"
    LOCAL = "local"
    CUSTOM = "custom"


# ========== AI 模型配置 Schema ==========
class AIModelConfigBase(BaseModel):
    name: str
    model_type: ModelType
    provider: ModelProvider
    base_url: Optional[str] = None
    model_name: str
    extra_config: Dict[str, Any] = {}


class AIModelConfigCreate(AIModelConfigBase):
    api_key: Optional[str] = None


class AIModelConfigUpdate(BaseModel):
    name: Optional[str] = None
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    model_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None
    extra_config: Optional[Dict[str, Any]] = None


class AIModelConfigSchema(AIModelConfigBase):
    id: str
    api_key: Optional[str] = None
    is_active: bool
    is_default: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ========== 岗位管理 Schema ==========
class ScoreRule(BaseModel):
    dimension: str
    weight: int
    criteria: List[Dict[str, Any]]


class JobCreate(BaseModel):
    title: str
    department: Optional[str] = None
    jd_content: str
    score_rules: Optional[List[ScoreRule]] = []


class JobUpdate(BaseModel):
    title: Optional[str] = None
    department: Optional[str] = None
    jd_content: Optional[str] = None
    status: Optional[str] = None
    score_rules: Optional[List[ScoreRule]] = None


class JobSchema(BaseModel):
    id: str
    title: str
    department: Optional[str]
    jd_content: str
    jd_file_path: Optional[str]
    status: str
    score_rules: List[Dict]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class JobDetailSchema(JobSchema):
    resume_count: int = 0


# ========== 简历管理 Schema ==========
class UploadResponse(BaseModel):
    task_ids: List[str]
    message: str = "上传成功"


class ResumeSchema(BaseModel):
    id: str
    job_id: str
    candidate_name: Optional[str]
    file_path: str
    file_type: str
    file_size: int
    status: str
    status_progress: int
    status_message: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ResumeDetailSchema(ResumeSchema):
    parsed_content: Optional[Dict] = None
    matching_result: Optional[Dict] = None
    interview_questions: Optional[List[Dict]] = None


# ========== 匹配结果 Schema ==========
class DimensionScore(BaseModel):
    dimension: str
    score: float
    max_score: float
    evidence: List[str]


class MatchingResultSchema(BaseModel):
    id: str
    resume_id: str
    total_score: float
    recommendation: str
    summary: str
    analysis_report: str
    dimension_scores: List[DimensionScore]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ========== 面试题目 Schema ==========
class InterviewQuestionSchema(BaseModel):
    id: str
    resume_id: str
    question: str
    answer: str
    category: str
    difficulty: str
    sort_order: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ========== 人才库 Schema ==========
class TalentPoolSchema(BaseModel):
    id: str
    resume_id: str
    candidate_name: Optional[str]
    current_company: Optional[str]
    current_position: Optional[str]
    years_of_experience: Optional[int]
    highest_education: Optional[str]
    major: Optional[str]
    skills: Optional[List[str]]
    best_score: Optional[float]
    best_match_job: Optional[str]
    status: str
    tags: List[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class TalentPoolDetailSchema(TalentPoolSchema):
    phone: Optional[str]
    email: Optional[str]
    job_history: Optional[List[Dict]]
    notes: Optional[str]
    interactions: Optional[List[Dict]] = []


class TalentPoolCreate(BaseModel):
    resume_id: str


class AddTalentTags(BaseModel):
    tags: List[str]


class UpdateTalentNotes(BaseModel):
    notes: str
