# 快速使用

### 配置环境

```bash
uv venv  -p 3.11
source .venv/bin/activate
python -m ensurepip --upgrade
uv pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple
python -m playwright install

```

### 脚本录制

```bash
playwright codegen --target python -b firefox  https://example.com
```

### demo示例

```bash
python douyin_chat_send_demo.py
```

