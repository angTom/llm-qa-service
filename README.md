# llm-qa-service   大模型调用服务 (电商运营AI助手后端项目)
## 项目背景
基于FastAPI +DeepSeek LLM构建的企业级电商运营问答后端
提供RESFTful `/chat`对话接口，支持多轮对话, API_Key接口鉴权, Prompt注入防护,输入长度校验, LLM调用重试, 结构化日志, 全局异常处理!
> 学习项目: 大模型应用开发, 用于ToB客服类LLM服务练习!
## 技术栈
- Python 3.13
- uv (包管理+虚拟环境)
- FastAPI 接口框架
- openai sdk (兼容DeepSeek接口)
- tenactity: 接口重试 (指数退避)
- pydantic: 请求参数校验
python-dotenv: 环境变量管理
- logging: 结构化日志
## 项目结构
llm-qa-service/
├── .env # 大模型配置文件（本地开发用，不要提交到Git）
├── .env.example # 配置模板文件
├── app/
│   ├── main.py           # 入口，组装路由
│   ├── routers/chat.py   # 问答接口
│   ├── services/llm.py   # 模型调用（第1周代码搬进来）
│   ├── schemas/          # Pydantic模型
│   ├── core/config.py    # 配置读取（pydantic-settings读.env）
│   └── core/logging.py   # 日志配置
├── logs/                 # 日志文件
├── pyproject.toml        # 项目依赖
├── uv.lock               # 项目依赖锁文件
├── .gitignore            # Git忽略文件
└── README.md             # 项目说明
