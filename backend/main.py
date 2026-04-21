from fastapi import FastAPI
from app.api import app
from app.database import init_db

# 初始化数据库
init_db()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
