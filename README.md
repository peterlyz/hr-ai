# HR AI 招聘助手

一个面向招聘场景的智能辅助系统，用于管理岗位 JD、批量上传简历、按岗位规则进行 AI 评分筛选，并为通过筛选的候选人自动生成面试题和报告。

## 项目目标

基于原始需求，项目围绕以下主流程构建：

1. 上传多个岗位 JD。
2. 按岗位 JD 生成或维护评分规则。
3. 为岗位批量上传简历并解析内容。
4. 对简历进行 AI 评分和筛选。
5. 为通过筛选的候选人生成 15-20 道面试题及参考答案。
6. 将评分报告和面试题报告持久化并支持下载。

## 当前功能

### 已完成

- 岗位管理
  - 新建岗位
  - 上传 JD 文件
  - AI 生成评分规则
  - 手工编辑评分规则和通过分数线
- 简历管理
  - 批量上传 PDF / Word / TXT / Markdown 简历
  - 文件解析为结构化文本
  - 按岗位批量评分
  - 分页、搜索、筛选简历列表
- 评分流程
  - 基于岗位评分规则输出维度评分明细
  - 后端按规则重算总分，避免直接信任模型总分
  - 输出综合评价、优势、不足
- 面试题流程
  - 仅对通过筛选的候选人生成面试题
  - 生成 15-20 道题目，不足时自动重试一次
- 任务追踪
  - 已支持任务流水持久化
  - 覆盖评分规则生成、简历解析、简历评分、面试题生成
  - 页面可查看最近任务状态
- 报告能力
  - 评分报告 PDF 下载
  - 面试题报告 PDF 下载
  - 报告生成记录和下载次数持久化
- 数据展示
  - 岗位数据大屏
  - 分数分布
  - Top 候选人
- 实时反馈
  - WebSocket 推送简历解析、评分、面试题生成进度

### 当前仍是开发 / 演示模式

- 默认管理员账号会在启动时自动创建：`admin / admin123`
- 配置存储在数据库中，适合本地演示和开发，不适合作为生产方案直接使用
- 前端构建已通过，但仍存在较大的打包体积警告，后续需要做 chunk 拆分优化

## 技术栈

### 前端

- Vue 3
- TypeScript
- Vite
- Pinia
- Vue Router
- Element Plus
- ECharts
- Axios

### 后端

- FastAPI
- SQLAlchemy
- Pydantic Settings
- OpenAI 兼容接口
- MarkItDown
- ReportLab
- SQLite

## 项目结构

```text
hr-ai/
├─ backend/
│  ├─ app/
│  │  ├─ models/          # 数据模型
│  │  ├─ routers/         # API 路由
│  │  ├─ services/        # 业务服务、AI 调用、任务流水
│  │  ├─ utils/           # 文件解析、安全等工具
│  │  ├─ config.py
│  │  ├─ database.py
│  │  └─ main.py
│  ├─ uploads/            # 上传文件目录
│  ├─ reports/            # 生成报告目录
│  ├─ requirements.txt
│  └─ hr_ai.db            # 本地 SQLite 数据库
├─ frontend/
│  ├─ src/
│  │  ├─ api/
│  │  ├─ components/
│  │  ├─ composables/
│  │  ├─ router/
│  │  ├─ stores/
│  │  ├─ types/
│  │  └─ views/
│  ├─ package.json
│  └─ vite.config.ts
├─ docs/
│  └─ 需求.txt
└─ README.md
```

## 核心数据模型

- `jobs`
  - 岗位、JD 正文、通过线、状态
- `scoring_rules`
  - 岗位评分维度、权重、评分说明、满分
- `resumes`
  - 简历文件、解析状态、解析结果
- `evaluations`
  - 简历评分结果、维度明细、面试题生成状态
- `interview_questions`
  - 面试题、难度、类型、参考答案
- `pipeline_tasks`
  - 任务流水，记录每个阶段任务状态
- `report_records`
  - 报告生成记录、文件路径、下载次数
- `system_configs`
  - 模型 API 配置

## 任务状态说明

当前系统已经将任务状态持久化到 `pipeline_tasks`，主要任务类型包括：

- `job_rule_generation`
  - 岗位评分规则生成
- `resume_parse`
  - 简历解析
- `resume_evaluation`
  - 简历评分
- `interview_generation`
  - 面试题生成

通用状态包括：

- `pending`
- `processing`
- `done`
- `failed`
- `skipped`

## 本地启动

### 1. 启动后端

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

后端默认地址：

- `http://127.0.0.1:8000`
- 健康检查：`http://127.0.0.1:8000/api/health`

### 2. 启动前端

```powershell
cd frontend
npm install
npm run dev
```

前端默认地址：

- `http://127.0.0.1:5173`

前端开发环境已配置代理：

- `/api` -> `http://localhost:8000`
- `/ws` -> `ws://localhost:8000`

## 系统配置

系统支持在页面中配置 OpenAI 兼容接口，主要配置项包括：

- `llm_api_base`
- `llm_api_key`
- `llm_model_name`
- `llm_max_tokens`

默认配置存储在数据库 `system_configs` 表中。

## 运行与验证

### 后端编译检查

```powershell
python -m compileall backend\app
```

### 前端构建检查

```powershell
cd frontend
npm run build
```

### 数据库自动初始化

后端启动时会自动执行：

- 创建表结构
- 补齐历史开发阶段新增字段
- 创建默认管理员账号
- 创建上传目录和报告目录

## 当前页面

- 登录页
- 岗位列表页
- 岗位创建页
- 岗位详情页
- 简历管理页
- 评分详情页
- 面试题页
- 数据大屏页
- 系统设置页

## 已完成的关键优化

- 修复前端类型问题，保证 `npm run build` 可通过
- 后台任务不再复用请求期数据库会话
- 面试题生成状态持久化
- 增加统一任务流水表
- 简历列表支持分页、搜索、筛选
- 增加报告记录表，支持下载次数统计
- WebSocket 使用当前站点地址，不再写死 `localhost:8000`

## 后续建议

- 优化前端打包体积，拆分大 chunk
- 为任务流水增加独立页面或时间线视图
- 增加报告列表页，而不是只在详情页查看
- 补充更多自动化测试
- 将 SQLite 升级为更适合并发场景的数据库
- 引入真正的任务队列系统，替代当前应用内后台任务

## 说明

`frontend/README.md` 目前仍是 Vite 模板占位文档，项目说明以根目录本文件为准。
