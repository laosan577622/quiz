from flask import Flask, request, jsonify, render_template
import json
import configparser
import openai

app = Flask(__name__)

# 初始化配置解析器并读取config.ini文件，用于获取OpenAI的API密钥和基础URL
config = configparser.ConfigParser()
config.read('config.ini')

# 从配置文件中获取OpenAI的API密钥和基础URL，并设置到openai模块中
api_key = config['openai']['api_key']
openai.api_key = api_key
openai.api_base = config['openai']['base_url']
model = config['openai']['model']

# 读取题目文件
def read_questions(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        questions = json.load(file)
        return questions

# 判断答案是否正确
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

# 提交错题给ChatGPT进行讲解
def submit_to_chatgpt(question):
    prompt = f"请你扮演一名严格的家教老师，现在，你的学生做错了这一题，请解释以下题目并给出正确答案：\n\n题目：{question['content']}\n答案：{question['answer']}"
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response['choices'][0]['message']['content']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_questions', methods=['GET'])
def get_questions():
    questions = read_questions('exam_questions.json')
    return jsonify(questions)

@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    data = request.json
    question = data['question']
    user_answer = data['answer']
    is_correct = judge_answer(question, user_answer)
    return jsonify({'correct': is_correct})

@app.route('/explain', methods=['POST'])
def explain():
    data = request.json
    question = data['question']
    explanation = submit_to_chatgpt(question)
    return jsonify({'explanation': explanation})

if __name__ == '__main__':
    print("\nPlease make sure you have set up the config.ini file correctly.")
    print("\nServer started,plaease visit http://localhost:5000 to use the app.") 
    print('\nIf you don\'t like the theme, you can change it in the /templates/index.html file.')
    print('\nYour API key is:', api_key,'\nYour base URL is:', openai.api_base,'\nThe model you want to use is:', model,'\n Is it correct?')
    app.run(debug=True)
