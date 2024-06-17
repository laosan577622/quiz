import json
import openai
import configparser

# 初始化配置解析器并读取config.ini文件，用于获取OpenAI的API密钥和基础URL
config = configparser.ConfigParser()
config.read('config.ini')
api_key = config['openai']['api_key']
openai.api_key = api_key
openai.api_base = config['openai']['base_url']
model = config['openai']['model']

def get_questions(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        questions = json.load(file)
        return questions

def judge_answer(question, user_answer):
    requirement = question['requirement']
    correct_answer = question['answer']
    if requirement == '简答_包含关键字':
        return correct_answer in user_answer
    elif requirement == '简答_完全符合':
        return user_answer == correct_answer
    elif requirement == '选择_单选':
        return user_answer.upper() == correct_answer
    else:
        return False

def stream_to_chatgpt(question):
    prompt = f"请解释以下题目并给出正确答案：\n\n题目：{question['content']}\n答案：{question['answer']}"
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        stream=True
    )

    def generate():
        for chunk in response:
            if 'choices' in chunk:
                yield f"data: {chunk['choices'][0]['delta']['content']}\n\n"

    return generate()
