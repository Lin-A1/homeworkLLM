# homeworkLLM
基于ollama+langchain的大模型作业评审任务

## 功能特点
- 智能作业评审
- 自动化模型调配
- 简便的环境配置流程

## 模型调配
- **[demo.ipynb](demo.ipynb)**
- **[demo.py](demo.py)**


## 环境配置
- **ollama**
```shell
curl -fsSL https://ollama.com/install.sh | sh
```
- **python**
```shell
conda create -n yourProjectName python=3.10
conda activate yourProjectName
pip install -r requirements.txt
```

- **model**
```shell
# download model

cd  model/qwen2.5
ollama create hwllm-qwen2.5 -f Modelfile
cd ../qwen2.5-coder
ollama create hwllm-qwen2.5-coder -f Modelfile
```

## 技术栈
### - **`fastapi`+`tortoise`**
  待更新

### - **`vue3`**
  待更新

### - **`ollama`+`langchina`**
  待更新