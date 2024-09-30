from fastapi import FastAPI
from codeApi import review_code_router  # 导入代码审查路由

"""
start by `uvicorn main:app --reload`
"""

app = FastAPI()

app.include_router(review_code_router, prefix="/code_review", tags=["Code Review"])

@app.get("/")
async def root():
    return {"message": "Welcome to my HWAPI!"}

