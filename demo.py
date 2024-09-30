import json
import warnings

from langchain.memory import ConversationBufferMemory
from langchain_community.llms import Ollama
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate

warnings.filterwarnings("ignore")


class CodeReview:
    def __init__(self, model_name, require, code_content):
        self.model = Ollama(model=model_name)
        self.require = require
        self.code_content = code_content
        self.system_content = """您是编程教育领域的专家，具有丰富的编程知识和教育经验。您愿意帮助学生进行代码的审查。

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
                with open('error.log', 'a') as log_file:
                    log_file.write(f"code error occurred: {e}\n")
                continue


class ExperimentReportReviewer:
    def __init__(self, model_name, json_path):
        self.model = Ollama(model=model_name)
        self.data = self.load_data(json_path)
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


# 代码审查使用示例
require = "反转字符串中的字符"
code_content = """
class ReverseString(object):
    def reverse(self, chars):
        if chars:
            size = len(chars)
            for i in range(size // 2):
                chars[i], chars[size - 1 - i]  = chars[size - 1 - i], chars[i]
        return chars
"""

code_reviewer = CodeReview(model_name="hwllm-qwen2.5-coder", require=require, code_content=code_content)
result = code_reviewer.review_code()
print(result)

# 实验报告审查使用示例
json_path = 'data/test.json'
reviewer = ExperimentReportReviewer(model_name="hwllm-qwen2.5", json_path=json_path)
result = reviewer.review_experiment()
print(result)
