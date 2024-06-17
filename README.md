# Flask 问答应用程序

这是一个基于 Flask 的问答系统 web 应用程序。该应用程序允许用户回答问题，提交答案，并使用 OpenAI 的 ChatGPT 模型获取错误答案的解释。

## 程序截图
![](https://cloud.577622.xyz/d/%E6%9C%AC%E6%9C%BA%E5%AD%98%E5%82%A8/github/quiz/%E5%B1%8F%E5%B9%95%E6%88%AA%E5%9B%BE%202024-06-17%20073443.png?sign=TrHXOMVGUvD4tFf-NW-vCww58VdS1Li5LHcs3--XF94=:0)

## 功能

- 获取并显示问答问题。
- 提交答案并立即收到反馈。
- 跟踪正确和错误的答案。
- 使用 ChatGPT 请求错误答案的解释。

## 前提条件

- Python 3.7 或更高版本
- Flask
- OpenAI Python 客户端库

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
    [openai]
    api_key = YOUR_OPENAI_API_KEY
    base_url = https://api.openai.com/v1
    ```

    将 `YOUR_OPENAI_API_KEY` 替换为你的实际 OpenAI API 密钥。

2. 确保在根目录下有一个问题文件（例如 `questions.json`），格式如下：

    ```json
    [
        {
            "number": "1",
            "content": "test1",
            "answer": "1",
            "requirement": "简答_包含关键字"
        },
        {
            "number": "2",
            "content": "测试题目二",
            "answer": "2",
            "requirement": "简答_完全符合"
        },
        {
            "number": "3",
            "content": "3",
            "answer": "3",
            "requirement": "简答_包含关键字"
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
- 点击“查看错题讲解”按钮请求 ChatGPT 的解释。

## 前端代码

前端代码包含在 `templates` 目录下的 `index.html` 文件中。主要结构如下：

```html
<!DOCTYPE html>
<html lang="cn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>老三AI问答 Web</title>
    <style>
        /* 你的 CSS 样式 */
    </style>
</head>
<body>
    <div class="container">
        <h1>老三AI问答 Webui</h1>
        <div id="quiz"></div>
        <div id="result" class="result"></div>
    </div>
    <script>
        // 你的 JavaScript 代码
    </script>
</body>
</html>
```

## API 端点

- `GET /get_questions`：获取问答问题列表。
- `POST /submit_answer`：提交答案并返回答案是否正确。
- `POST /explain`：请求 ChatGPT 对错误答案的解释。

