# 导入必要的库，包括json用于处理JSON格式数据，configparser用于读取配置文件，openai用于访问OpenAI API
import json
import configparser
import openai

# 初始化配置解析器并读取config.ini文件，用于获取OpenAI的API密钥和基础URL
# 读取配置文件
config = configparser.ConfigParser()
config.read('config.ini')

# 从配置文件中获取OpenAI的API密钥和基础URL，并设置到openai模块中
# 配置OpenAI
api_key = config['openai']['api_key']
openai.api_key = api_key
openai.api_base = config['openai']['base_url']
model = config['openai']['model']

# 读取题目文件，返回JSON格式的题目数据
# 读取题目文件
def read_questions(file_path):
    """
    读取指定路径的JSON格式题目文件，并返回解析后的题目数据列表。
    
    参数:
    file_path (str): 题目文件的路径。
    
    返回:
    list: 包含题目数据的列表，每个元素是一个字典。
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        questions = json.load(file)
        return questions

# 判断用户答案是否正确
# 判断答案是否正确
def judge_answer(question, user_answer):
    """
    根据题目的要求判断用户答案是否正确。
    
    参数:
    question (dict): 题目数据字典，包含要求和正确答案。
    user_answer (str): 用户的答案。
    
    返回:
    bool: 用户答案是否正确的布尔值。
    """
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

# 计算正确率
# 计算正确率
def calculate_accuracy(correct_count, total_questions):
    """
    计算正确率。
    
    参数:
    correct_count (int): 正确题目数量。
    total_questions (int): 总题目数量。
    
    返回:
    float: 正确率，百分比形式。
    """
    if total_questions == 0:  # 防止除零错误
        return 0.0
    else:
        return (correct_count / total_questions) * 100

# 提交错题给ChatGPT进行讲解
# 提交错题给ChatGPT进行讲解
def submit_to_chatgpt(question):
    """
    将题目提交给ChatGPT进行讲解。
    
    参数:
    question (dict): 题目数据字典。
    
    返回:
    str: ChatGPT返回的讲解内容。
    """
    prompt = f"请解释以下题目并给出正确答案：\n\n题目：{question['content']}\n答案：{question['answer']}"
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response['choices'][0]['message']['content']

# 主函数，执行程序的主要逻辑
def main():
    # 读取题目文件
    question_file_path = 'exam_questions.json'
    questions = read_questions(question_file_path)
    
    correct_count = 0
    incorrect_questions = []
    
    # 遍历题目，与用户交互，判断答案是否正确
    for question in questions:
        print(f"题目 {question['number']}：")
        print(question['content'])  # 直接打印题目内容，保留换行
        if 'options' in question:
            print("选项：")
            for option in question['options']:
                print(option)
        user_answer = input("请输入你的答案：")
        if judge_answer(question, user_answer):
            print("回答正确！")
            correct_count += 1
        else:
            print("回答错误！")
            print(f"正确答案是：{question['answer']}")
            incorrect_questions.append(question)
    
    total_questions = len(questions)
    accuracy = calculate_accuracy(correct_count, total_questions) 
    # 输出总体成绩和正确率
    print(f"你总共回答了 {total_questions} 道题目，其中 {correct_count} 道回答正确。")
    print(f"因此，你的正确率为：{accuracy:.2f}%。")
    
    # 如果有回答错误的题目，向ChatGPT请求讲解
    
    if incorrect_questions:
        view_explanations = input("\n你有错题。是否需要查看错题讲解？ (y/n): ").strip().lower()
        if view_explanations == 'y':
            print("\n请稍候，正在向ChatGPT请求讲解...请确保您已经在config.ini中配置了OpenAI的API密钥和基础URL。")
            for question in incorrect_questions:
                explanation = submit_to_chatgpt(question)
                print(f"\n题目 {question['number']}：")
                print(question['content'])
                if 'options' in question:
                    print("选项：")
                    for option in question['options']:
                        print(option)
                print(f"正确答案是：{question['answer']}")
                print("ChatGPT的讲解：")
                print(explanation)

# 当作为主模块运行时，执行主函数
# 运行主程序
if __name__ == '__main__':
    main()