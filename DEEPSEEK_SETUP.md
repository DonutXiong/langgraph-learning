# DeepSeek 配置指南

本文档指导你如何配置 LangGraph 学习项目以使用 DeepSeek 模型。

## 步骤 1: 获取 DeepSeek API Key

1. 访问 [DeepSeek 平台](https://platform.deepseek.com/)
2. 注册或登录账户
3. 进入 [API Keys 页面](https://platform.deepseek.com/api_keys)
4. 点击 "Create new secret key" 创建新的 API Key
5. 复制生成的 API Key（注意：只显示一次，请妥善保存）

## 步骤 2: 配置环境文件

项目已提供 `.env` 文件，你只需要：

1. 打开 `.env` 文件
2. 找到 `OPENAI_API_KEY=your_deepseek_api_key_here` 这一行
3. 将 `your_deepseek_api_key_here` 替换为你的实际 API Key

示例：
```env
OPENAI_API_KEY=sk-1234567890abcdef1234567890abcdef
```

## 步骤 3: 验证配置

运行以下命令验证配置是否正确：

```bash
python examples/03_tool_calling_agent.py
```

如果配置正确，你将看到类似以下的输出：
```
LLM 调用次数: 1

Human: 先算 (3 + 4) * 5，再除以 7，最后告诉我结果。
AI: 让我逐步计算...
```

## 配置说明

### 主要配置项

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `LANGCHAIN_MODEL` | `openai:deepseek-chat` | 使用的模型名称 |
| `OPENAI_API_KEY` | (需要填写) | DeepSeek API Key |
| `OPENAI_BASE_URL` | `https://api.deepseek.com` | DeepSeek API 地址 |

### 可选配置项

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `LANGSMITH_TRACING` | `false` | 是否启用 LangSmith 追踪 |
| `LANGSMITH_API_KEY` | (空) | LangSmith API Key |
| `LANGSMITH_PROJECT` | `langgraph-learning` | LangSmith 项目名称 |

## 故障排除

### 常见问题

1. **API Key 错误**
   ```
   运行失败: 检测到 OpenAI 兼容模型，但未配置 OPENAI_API_KEY。
   ```
   **解决方案**: 检查 `.env` 文件中的 `OPENAI_API_KEY` 是否已正确设置。

2. **网络连接问题**
   ```
   ConnectionError: 无法连接到 DeepSeek API
   ```
   **解决方案**: 检查网络连接，确保可以访问 `https://api.deepseek.com`

3. **额度不足**
   ```
   Error: Insufficient quota
   ```
   **解决方案**: 检查 DeepSeek 账户余额或免费额度

4. **模型不可用**
   ```
   Error: Model not found
   ```
   **解决方案**: 检查 `LANGCHAIN_MODEL` 设置，DeepSeek 支持的模型包括：
   - `deepseek-chat` (默认)
   - `deepseek-coder`
   - 其他 DeepSeek 模型

### 测试连接

你可以使用以下 Python 代码测试 DeepSeek API 连接：

```python
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com")
)

try:
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": "Hello"}],
        max_tokens=10
    )
    print("连接成功!")
    print(f"响应: {response.choices[0].message.content}")
except Exception as e:
    print(f"连接失败: {e}")
```

## 高级配置

### 使用其他 DeepSeek 模型

如果你想使用其他 DeepSeek 模型，修改 `.env` 文件中的 `LANGCHAIN_MODEL`：

```env
# 使用 DeepSeek Coder
LANGCHAIN_MODEL=openai:deepseek-coder

# 或其他支持的模型
```

### 调整模型参数

在 `examples/03_tool_calling_agent.py` 中，你可以调整模型参数：

```python
# 修改 temperature 参数（默认 0）
model_config = {
    "model": model_name,
    "temperature": 0.7,  # 更高的温度 = 更有创意的输出
    "max_tokens": 1000,  # 最大输出长度
}
```

## 注意事项

1. **API Key 安全**: 不要将 `.env` 文件提交到版本控制系统
2. **额度限制**: DeepSeek 有免费额度，注意使用量
3. **速率限制**: API 有调用频率限制
4. **模型版本**: 确保使用的模型名称是 DeepSeek 当前支持的

## 获取帮助

如果遇到问题：

1. 查看 [DeepSeek 官方文档](https://platform.deepseek.com/api-docs/)
2. 检查项目 [GitHub Issues](https://github.com/your-repo/langgraph-learning/issues)
3. 在社区论坛提问

## 更新日志

- **2026-04-08**: 初始版本，支持 DeepSeek 配置