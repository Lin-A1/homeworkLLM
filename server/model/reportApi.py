from fastapi import APIRouter, HTTPException
from fastapi import Request
import json
from langchain_community.llms import Ollama
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory

import logging
import warnings

logging.basicConfig(level=logging.INFO)
warnings.filterwarnings("ignore")

experiment_review_router = APIRouter()


class ExperimentReportReviewer:
    def __init__(self, data):
        self.model = Ollama(model='hwllm-qwen2.5')
        self.data = data
        self.system_content = """您是编程教育领域的专家，具有丰富的编程知识和教育经验。您需要进行实验报告的批改并给出得分与评语。

        ### 输出要求
        - **评分（满分 100 分）**
        - **评语需要给出依据，若学生做的不好，可以提出问题所在**：
        - **甄别学生实验内容与要求是否相符**
        - **对学生的评阅要求尽量宽松，**
        - **对学生的实验内容和实验要求不符可以给他低分**
        - **对描述详细的实验报告可以给出更高的评分**
        - **确保输出是紧凑格式的有效 JSON 对象，不包含任何其他解释、转义符、换行符或反斜杠**
        """
        self.prompt_template = ChatPromptTemplate.from_messages(
            [("system", self.system_content), ("user", "{text}")]
        )
        self.parser = JsonOutputParser()
        self.chain = self.prompt_template | self.model | self.parser
        self.memory = ConversationBufferMemory(return_messages=True)

    def load_data(self, json_path):
        with open(json_path, 'r', encoding='utf8') as fp:
            return json.load(fp)

    def get_true_key_in_chinese(self, experiment_dict):
        key_to_chinese = {
            "basic_experiment": "基础实验",
            "professional_experiment": "专业实验",
            "comprehensive_experiment": "综合实验"
        }
        for key, value in experiment_dict.items():
            if value:
                return key_to_chinese.get(key, "未知实验")
        return "未知实验"

    def generate_work_content(self):
        return f"""
        本次{self.data["experiment_details"]["experiment_project_name"]}实验是{self.data["course_info"]["course_name"]}课程的{self.get_true_key_in_chinese(self.data['course_info']['experiment_type'])},
        本次实验目的是{self.data['experiment_purpose_and_requirements']['purpose']},本次实验要求是{self.data['experiment_purpose_and_requirements']['requirements']},以下为实验报告：
        实验原理为：{self.data['experiment_principle_methods_steps']['principle']}
        实验方法为：{self.data['experiment_principle_methods_steps']['methods']}
        实验步骤为：{self.data['experiment_principle_methods_steps']['steps']}
        实验内容为：{self.data['experiment_content_and_data']['content']}
        实验结果为：{self.data['experiment_content_and_data']['results']}
        实验心得体会为：{self.data['experiment_reflection']['experience']}
        """

    def review_experiment(self):
        work_content = self.generate_work_content()
        self.memory.save_context({"input": work_content}, {"output": "好的，我知道了"})
        self.memory.load_memory_variables({})

        experiment_name = self.data["experiment_details"]["experiment_project_name"]
        frequency = 0
        while True:
            try:
                response = self.chain.invoke({"text": f"对实验{experiment_name}进行评分与评价"})
                if isinstance(response, dict):
                    return response
            except Exception as e:
                frequency += 1
                if frequency > 5:
                    return False
                with open('error.log', 'a') as log_file:
                    log_file.write(f"Experiment error occurred: {e}\n")
                continue


@experiment_review_router.post("/")
async def review_experiment(request: Request):
    logging.info("start review_code")
    request_data = await request.json()
    reviewer = ExperimentReportReviewer(request_data['data'])
    result = reviewer.review_experiment()
    if result is False:
        raise HTTPException(status_code=500, detail="Error during experiment review")
    return result
