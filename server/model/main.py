from fastapi import FastAPI
from codeApi import review_code_router  # 导入代码审查路由
from reportApi import experiment_review_router

"""
cd server/model/
start by `uvicorn main:app --reload`
"""

app = FastAPI()

app.include_router(review_code_router, prefix="/code_review", tags=["Code Review"])
app.include_router(experiment_review_router, prefix="/experiment_review", tags=["Experiment Review"])


@app.get("/")
async def root():
    return {"message": "Welcome to my HWAPI!"}
