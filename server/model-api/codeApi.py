from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import warnings
from langchain_community.llms import Ollama
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate

warnings.filterwarnings("ignore")

review_code_router = APIRouter()


class CodeReviewRequest(BaseModel):
    require: str
    code_content: str


class CodeReview:
    def __init__(self, require, code_content):
        self.model = Ollama(model='hwllm-qwen2.5-coder')
        self.require = require
        self.code_content = code_content
        self.system_content = """您的编程教育领域的专家，具有丰富的编程知识和教育经验。您愿意帮助学生进行代码的审查。

        ### 输出要求
        - **评分（满分 100 分）**
        - **评语中写出代码问题或优化建议**：
        - **甄别学生的代码质量，并判断是否有错误**
        - **甄别学生的代码是否能实现功能**
        - **假如学生代码是基本符合的，对学生的代码要求尽量宽松，假如学生满足了代码要求，并且没有过分的性能错误，尽量给出95以上的高分甚至满分****
        - **假如学生代码不合要求或者不是代码可以给他低分**

        代码要实现的功能是{require}
        """
        self.prompt_template = ChatPromptTemplate.from_messages(
            [("system", self.system_content), ("user", "{text}")]
        )
        self.parser = JsonOutputParser()
        self.chain = self.prompt_template | self.model | self.parser

    def review_code(self):
        frequency = 0
        while True:
            try:
                response = self.chain.invoke({"require": self.require, "text": self.code_content})
                if isinstance(response, dict):
                    return response
            except Exception as e:
                frequency += 1
                if frequency > 5:
                    return False
                continue


@review_code_router.post("/")
async def review_code(request: CodeReviewRequest):
    code_review = CodeReview(request.model_name, request.require, request.code_content)
    result = code_review.review_code()
    if result is False:
        raise HTTPException(status_code=500, detail="Error during code review")
    return result
