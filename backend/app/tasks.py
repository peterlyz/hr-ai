import threading
import logging
from typing import Optional
from .database import SessionLocal
from . import models, services
from .ai import ai_client
from .parser import MarkItDownParser

logger = logging.getLogger(__name__)


class SimpleTaskQueue:
    """简单的任务队列（线程池）"""
    
    def __init__(self, max_workers: int = 3):
        self.max_workers = max_workers
        self.semaphore = threading.Semaphore(max_workers)
    
    def submit(self, func, **kwargs):
        """提交任务"""
        def worker():
            try:
                with self.semaphore:
                    func(**kwargs)
            finally:
                pass
        
        thread = threading.Thread(target=worker)
        thread.daemon = True
        thread.start()
        return thread


task_queue = SimpleTaskQueue(max_workers=3)


def process_resume(resume_id: str):
    """处理简历（包含两阶段任务）"""
    db = SessionLocal()
    try:
        resume = db.query(models.Resume).get(resume_id)
        if not resume:
            logger.error(f"简历不存在：{resume_id}")
            return
        
        services.update_resume_status(db, resume_id, "parsing", 10, "开始解析简历...")
        
        # ========== 阶段 1：文档解析 ==========
        try:
            parsed_content = MarkItDownParser.parse(resume.file_path)
            services.update_resume_status(db, resume_id, "parsed", 30, "解析完成", parsed_content=parsed_content)
        except Exception as e:
            logger.error(f"解析失败：{e}")
            services.update_resume_status(db, resume_id, "failed", 0, f"解析失败：{str(e)}")
            return
        
        # ========== 阶段 2：JD 匹配评分 ==========
        services.update_resume_status(db, resume_id, "matching", 40, "开始匹配 JD...")
        
        job = db.query(models.JobPosting).get(resume.job_id)
        if not job:
            services.update_resume_status(db, resume_id, "failed", 0, "关联岗位不存在")
            return
        
        try:
            ai_client_instance = ai_client
            
            # 调用 AI 评估
            matching_result = evaluate_resume(
                ai_client=ai_client_instance,
                jd_content=job.jd_content,
                score_rules=job.score_rules,
                resume_content=parsed_content
            )
            
            # 保存结果
            services.save_matching_result(db, resume.id, matching_result)
            
            if matching_result["total_score"] >= 60:
                services.update_resume_status(db, resume_id, "matched", 70, f"匹配通过 ({matching_result['total_score']}分)")
                
                # ========== 阶段 3：生成面试题目 ==========
                services.update_resume_status(db, resume_id, "generating_questions", 80, "生成面试题目...")
                
                questions = generate_interview_questions(
                    ai_client=ai_client_instance,
                    jd_content=job.jd_content,
                    resume_content=parsed_content,
                    matching_result=matching_result,
                    count=15
                )
                
                services.save_interview_questions(db, resume.id, questions)
                
                # ========== 阶段 4：加入人才库 ==========
                services.update_resume_status(db, resume_id, "adding_to_talent_pool", 90, "加入人才库...")
                try:
                    services.add_to_talent_pool(db, resume.id, job)
                except Exception as e:
                    logger.warning(f"加入人才库失败：{e}")
                
                services.update_resume_status(db, resume_id, "completed", 100, "处理完成")
            else:
                services.update_resume_status(db, resume_id, "completed", 100, f"匹配未通过 ({matching_result['total_score']}分)")
                
        except Exception as e:
            logger.error(f"AI 处理失败：{e}")
            services.update_resume_status(db, resume_id, "failed", 0, f"AI 处理失败：{str(e)}")
            
    except Exception as e:
        logger.error(f"任务执行失败：{e}")
        services.update_resume_status(db, resume_id, "failed", 0, f"系统错误：{str(e)}")
    finally:
        db.close()


def evaluate_resume(ai_client, jd_content: str, score_rules: list, resume_content: dict) -> dict:
    """简历评估"""
    
    prompt = f"""
你是专业的招聘专家。请根据以下岗位 JD 和评分规则，对候选人简历进行评估打分。

## 岗位 JD
{jd_content}

## 评分规则
{str(score_rules)}

## 候选人简历
{str(resume_content)}

请按照以下格式返回评估结果（必须是有效的 JSON）：
{{
    "total_score": 85,
    "recommendation": "recommended",
    "summary": "简要总结",
    "analysis_report": "详细分析报告",
    "dimension_scores": [
        {{
            "dimension": "学历",
            "score": 25,
            "max_score": 30,
            "evidence": ["硕士学历，计算机专业"]
        }}
    ]
}}

recommendation 可选值：
- highly_recommended: 强烈推荐（总分≥85）
- recommended: 推荐（60≤总分<85）
- not_recommended: 不推荐（总分<60）

请直接返回 JSON，不要有其他文字。"""
    
    result_text = ai_client.chat(prompt)
    
    # 提取 JSON 部分
    import json
    start = result_text.find('{')
    end = result_text.rfind('}') + 1
    if start >= 0 and end > start:
        json_str = result_text[start:end]
        return json.loads(json_str)
    raise ValueError("AI 返回格式错误")


def generate_interview_questions(ai_client, jd_content: str, resume_content: dict, matching_result: dict, count: int = 15) -> list:
    """生成面试题目"""
    
    prompt = f"""
你是面试官。请根据以下 JD、简历和评估结果，生成针对性的面试题目。

## 岗位 JD
{jd_content}

## 候选人简历
{str(resume_content)}

## 评估结果
总分：{matching_result.get('total_score')}
评价：{matching_result.get('summary')}

请生成 {count} 个面试问题，包含：
- 技术能力题（40%）
- 行为面试题（30%）
- 文化匹配题（20%）
- 解决问题题（10%）

按照以下格式返回（必须是有效的 JSON 数组）：
[
    {{
        "question": "请介绍一下你在 XX 项目中的角色",
        "answer": "参考答案要点...",
        "category": "technical",
        "difficulty": "medium"
    }}
]

category 可选：technical, behavioral, cultural_fit, problem_solving
difficulty 可选：easy, medium, hard

请直接返回 JSON 数组，不要有其他文字。"""
    
    import json
    result_text = ai_client.chat(prompt)
    
    start = result_text.find('[')
    end = result_text.rfind(']') + 1
    if start >= 0 and end > start:
        json_str = result_text[start:end]
        return json.loads(json_str)
    raise ValueError("AI 返回格式错误")
