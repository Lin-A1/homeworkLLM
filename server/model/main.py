from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from codeApi import review_code_router  # 导入代码审查路由
from reportApi import experiment_review_router

"""
cd server/model/
start by `uvicorn main:app --reload`
"""

app = FastAPI()

# 配置跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 指定允许的域名
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有请求头
)

app.include_router(review_code_router, prefix="/code_review", tags=["Code Review"])
app.include_router(experiment_review_router, prefix="/experiment_review", tags=["Experiment Review"])


@app.get("/")
async def root():
    return {"message": "Welcome to my HWAPI!"}
