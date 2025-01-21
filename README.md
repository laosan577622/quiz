# Flask 问答应用程序

这是一个基于 Flask 的问答系统 web 应用程序。该应用程序允许用户回答问题，提交答案，并使用AI进行解释。


## 功能

- 获取并显示问答问题。
- 提交答案并立即收到反馈。
- 跟踪正确和错误的答案。
- 使用 ChatGPT 请求错误答案的解释。

## 前提条件

- Python 3.7 或更高版本
- Flask
- Zhipuai 客户端库

## 安装

1. 克隆仓库：

    ```sh
    git clone https://github.com/laosan577622/quiz.git
    cd quiz
    ```


2. 安装所需的包：

    ```sh
    pip install -r requirements.txt
    ```

## 配置

1. 在根目录下创建 `config.ini` 文件，内容如下：

    ```ini
    [glm]
    api_key = YOUR_OPENAI_API_KEY
    base_url = https://api.zhipuai.com/v1
    model = glm-4
    ```

    将 `YOUR_OPENAI_API_KEY` 替换为你的实际 智谱AI 密钥。

2. 确保在根目录下有一个问题文件（例如 `questions.json`），格式如下：

    ```json
[
        {
            "number": "1",
            "content": "冰变成水时是放出还是吸收热量？",
            "answer": "吸收",
            "requirement": "必须相同",
            "type": "简答"
        },
        {
            "number": "2",
            "content": "中国人民共和国在哪一年成立？",
            "options": ["1900", "1949", "1948", "1947"],
            "answer": "1949",
            "requirement": "选择_完全符合",
            "type": "选择"
        },
        {
            "number": "3",
            "content": "相较于python，C有什么优势？",
            "answer": "请根据用户回答自行判断，但必须有关于C语言的优势并且一定要比较",
            "requirement": "包含关键字",
            "type": "简答"
        }
        ]
    ```

## 运行应用程序

1. 启动 Flask 服务器：

    ```sh
    flask run
    ```

2. 打开浏览器并导航到 `http://127.0.0.1:5000` 访问问答应用程序。

## 使用方法

- 应用程序会逐个显示问答问题。
- 输入你的答案并点击“提交答案”按钮提交。
- 在所有问题回答完毕后，你会看到你的得分以及查看错误答案解释的选项。




## API 端点

- `GET /get_questions`：获取问答问题列表。
- `POST /submit_answer`：提交答案并返回答案是否正确。
- `POST /explain`：请求 ChatGPT 对错误答案的解释。

