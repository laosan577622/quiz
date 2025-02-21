import os
import random
from flask import Flask, request, jsonify, render_template, session
import json
import configparser
from zhipuai import ZhipuAI

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 设置一个密钥用于会话管理

# 确保 templates 文件夹存在
if not os.path.exists(os.path.join(app.root_path, 'templates')):
    os.makedirs(os.path.join(app.root_path, 'templates'))

# 初始化配置解析器并读取config.ini文件，用于获取GLM的API密钥和基础URL
config = configparser.ConfigParser()
config.read('config.ini')

# 从配置文件中获取GLM的API密钥，并设置到ZhipuAI客户端中
api_key = config['glm']['api_key']
client = ZhipuAI(api_key=api_key)
model = config['glm']['model']

# 读取题目文件
def read_questions(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        questions = json.load(file)
        return questions

# 写入题目文件
def write_questions(file_path, questions):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(questions, file, ensure_ascii=False, indent=4)

# 判断简答题答案是否正确
def judge_answer(question, user_answer):
    if question['type'] == '简答':
        return submit_to_chatgpt(question, user_answer)
    elif question['type'] == '选择':
        return user_answer.strip().lower() == question['answer'].strip().lower()
    return False

# 使用GLM模型判断简答题答案是否正确
def submit_to_chatgpt(question, user_answer):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是一个乐于解答各种问题的助手，你的任务是判断用户的答案是否正确，请尽量放低要求，答案即便过于简略也要算对，只要不是知识性错误，请都算作正确。并且，大多数学生习惯于使用词语回答而不是句子，请你理解但是如果遇到知识性错误，务必输出“错误”例如：吸收写成放出，错误写成正确之类"},
                {"role": "user", "content": f"题目 {question['number']}：{question['content']}\n类型是：{question['requirement']} \n 用户的答案是：{user_answer}\n 正确答案是：{question['answer']}\n请判断这个答案是否正确，并返回 '正确' 或 '错误'。注意：答案即便过于简略也要算对，只要不是知识性错误，请都算作正确。并且，大多数学生习惯于使用词语回答而不是句子，请你理解，请尽量放低要求。但是如果遇到知识性错误，务必输出“错误”例如：吸收写成放出，错误写成正确之类"}
            ],
        )
        return response.choices[0].message.content.strip().lower() == '正确'
    except Exception as e:
        print(f"Error in submit_to_chatgpt: {e}")
        return False

# 计算正确率
def calculate_accuracy(correct_count, total_questions):
    return (correct_count / total_questions) * 100 if total_questions > 0 else 0

# 提交错题给GLM进行讲解
def submit_to_chatgpt_explanation(question, user_answer):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你需要扮演一名老师，你的任务就是向您的学生进行错题讲解，请称呼用户为 同学。请不要使用markdown语法标点。"},
                {"role": "user", "content": f"题目 {question['number']}：{question['content']}\n类型是：{question['requirement']} \n 正确答案是：{question['answer']}\n用户的回答是：{user_answer}\n请解释这个答案，并指出用户的回答是否正确。不要使用Markdown语言。"}
            ],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error in submit_to_chatgpt_explanation: {e}")
        return "无法获取解释，请稍后再试。"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_questions', methods=['GET'])
def get_questions():
    questions = read_questions('exam_questions.json')
    # 随机排序选择题的选项
    for question in questions:
        if question['type'] == '选择' and 'options' in question:
            random.shuffle(question['options'])
    return jsonify(questions)

@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    data = request.json
    question = data['question']
    user_answer = data['user_answer']
    is_correct = judge_answer(question, user_answer)
    
    # 如果答案不正确，将错题信息存储在会话中
    if not is_correct:
        incorrect_questions = session.get('incorrect_questions', [])
        incorrect_questions.append({'question': question, 'user_answer': user_answer})
        session['incorrect_questions'] = incorrect_questions
    
    return jsonify({'is_correct': is_correct})

@app.route('/explain', methods=['POST'])
def explain():
    # 从会话中获取所有错题信息
    incorrect_questions = session.pop('incorrect_questions', [])
    
    explanations = []
    for item in incorrect_questions:
        question = item['question']
        user_answer = item['user_answer']
        explanation = submit_to_chatgpt_explanation(question, user_answer)
        explanations.append({'question': question, 'explanation': explanation})
    
    if explanations:
        return jsonify({'explanations': explanations})
    else:
        return jsonify({'explanation': '没有错题需要解释。'})

# 以下为题目增删改查的 API

# 新增题目
@app.route('/add_question', methods=['POST'])
def add_question():
    new_question = request.json
    questions = read_questions('exam_questions.json')
    questions.append(new_question)
    write_questions('exam_questions.json', questions)
    return jsonify({'message': '题目新增成功。'})

# 修改题目（根据题目 number 匹配）
@app.route('/update_question', methods=['PUT'])
def update_question():
    data = request.json
    question_number = data.get('number')
    if question_number is None:
        return jsonify({'error': '必须提供题目的 number 字段'}), 400
    try:
        question_number = int(question_number)
    except ValueError:
        return jsonify({'error': '题目编号必须为数字'}), 400

    questions = read_questions('exam_questions.json')
    updated = False
    for idx, question in enumerate(questions):
        try:
            q_num = int(question.get('number'))
        except (ValueError, TypeError):
            continue
        if q_num == question_number:
            questions[idx] = data
            updated = True
            break
    if updated:
        write_questions('exam_questions.json', questions)
        return jsonify({'message': '题目修改成功。'})
    else:
        return jsonify({'error': '未找到对应的题目'}), 404
# 删除题目（根据题目 number 匹配）
@app.route('/delete_question', methods=['DELETE'])
def delete_question():
    data = request.json
    question_number = data.get('number')
    if question_number is None:
        return jsonify({'error': '必须提供题目的 number 字段'}), 400
    try:
        question_number = int(question_number)
    except ValueError:
        return jsonify({'error': '题目编号必须为数字'}), 400
    questions = read_questions('exam_questions.json')
    new_questions = [q for q in questions if int(q.get('number')) != question_number]
    if len(new_questions) == len(questions):
        return jsonify({'error': '未找到对应的题目'}), 404
    write_questions('exam_questions.json', new_questions)
    return jsonify({'message': '题目删除成功。'})

# 修改配置文件 API
@app.route('/update_config', methods=['PUT'])
def update_config():
    data = request.json
    updated = False
    for section, keys in data.items():
        if not config.has_section(section):
            config.add_section(section)
        for key, value in keys.items():
            config.set(section, key, str(value))
            updated = True
    if updated:
        with open('config.ini', 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        return jsonify({'message': '配置文件修改成功。'})
    else:
        return jsonify({'error': '未提供有效的配置数据。'}), 400

if __name__ == '__main__':
    print("\n请确保已正确配置 config.ini 文件。")
    print("\n服务器已启动，请访问 http://localhost:5000 使用应用。")
    print("\n如果不喜欢当前主题，可在 /templates/index.html 文件中进行修改。")
    os.system('start http://localhost:5000')
    app.run(debug=True)