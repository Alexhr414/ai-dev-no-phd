# 用Python搞定多模态AI：让程序同时理解文字和图片

> 系列教程第三篇 | 前两篇：[AI聊天机器人](ai-chatbot-tutorial.md) → [RAG文档问答](rag-chatbot-tutorial.md) → **本篇：多模态AI**

## 这篇教什么？

上两篇我们搞了纯文本聊天和文档问答。但现实世界不只有文字——发票、截图、产品图、手写笔记……

这篇教你用Python构建一个**能同时理解图片和文字**的AI应用，成本几乎为零。

## 适合谁？

- 跟完前两篇的读者
- 想做图片分析/OCR/视觉问答的开发者
- 对多模态AI好奇的任何人

## 什么是多模态AI？

传统AI：输入文字 → 输出文字
多模态AI：输入文字+图片+音频+视频 → 输出文字+图片

2024年底开始，几乎所有主流模型都支持多模态了：
- **GPT-4o** — OpenAI的多模态旗舰
- **Claude 3.5 Sonnet** — Anthropic的视觉理解王者
- **Gemini 2.0** — Google的原生多模态模型
- **开源选择** — LLaVA, Qwen-VL, InternVL

## 环境准备

```bash
# 创建项目
mkdir multimodal-ai && cd multimodal-ai
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install openai pillow streamlit
```

你需要一个OpenAI API key（[platform.openai.com](https://platform.openai.com)获取）。

```bash
export OPENAI_API_KEY="sk-xxx"
```

## 第一步：基础图片理解

```python
# vision_basic.py
import openai
import base64
import sys

client = openai.OpenAI()

def analyze_image(image_path: str, question: str = "描述这张图片") -> str:
    """用GPT-4o分析图片"""
    
    # 读取并编码图片
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode()
    
    # 判断图片类型
    ext = image_path.lower().split(".")[-1]
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", 
            "gif": "image/gif", "webp": "image/webp"}.get(ext, "image/png")
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # 便宜！$0.15/1M input tokens
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": question},
                {"type": "image_url", "image_url": {
                    "url": f"data:{mime};base64,{image_data}"
                }}
            ]
        }],
        max_tokens=500
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "test.png"
    question = sys.argv[2] if len(sys.argv) > 2 else "这张图片里有什么？详细描述。"
    print(analyze_image(path, question))
```

运行：
```bash
python vision_basic.py photo.jpg "这张图里有几个人？他们在做什么？"
```

## 第二步：实用场景——发票/收据OCR

这是多模态AI最实用的场景之一：扔一张发票截图进去，自动提取结构化数据。

```python
# invoice_ocr.py
import openai
import base64
import json

client = openai.OpenAI()

def extract_invoice(image_path: str) -> dict:
    """从发票图片提取结构化数据"""
    
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode()
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": """分析这张发票/收据，提取以下信息并以JSON格式返回：
{
    "vendor": "商家名称",
    "date": "日期 (YYYY-MM-DD)",
    "items": [{"name": "商品名", "quantity": 数量, "price": 单价}],
    "subtotal": 小计,
    "tax": 税额,
    "total": 总计,
    "currency": "货币代码",
    "payment_method": "支付方式"
}
如果某项信息不存在，设为null。只返回JSON，不要其他文字。"""},
                {"type": "image_url", "image_url": {
                    "url": f"data:image/png;base64,{image_data}"
                }}
            ]
        }],
        max_tokens=1000,
        response_format={"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content)

# 使用
result = extract_invoice("receipt.png")
print(json.dumps(result, indent=2, ensure_ascii=False))
```

**成本**：一张发票约 $0.001（是的，不到1分钱）。

## 第三步：批量图片处理

```python
# batch_analyze.py
import openai
import base64
import json
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

client = openai.OpenAI()

def analyze_one(image_path: str, prompt: str) -> dict:
    """分析单张图片"""
    with open(image_path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{data}"}}
            ]}],
            max_tokens=300
        )
        return {"file": image_path, "result": resp.choices[0].message.content}
    except Exception as e:
        return {"file": image_path, "error": str(e)}

def batch_analyze(folder: str, prompt: str, max_workers: int = 5) -> list:
    """批量分析文件夹中的图片"""
    extensions = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
    images = [str(p) for p in Path(folder).iterdir() if p.suffix.lower() in extensions]
    
    print(f"找到 {len(images)} 张图片，开始分析...")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(analyze_one, img, prompt) for img in images]
        results = [f.result() for f in futures]
    
    return results

if __name__ == "__main__":
    results = batch_analyze(
        folder="./images",
        prompt="用一句话描述这张图片的内容"
    )
    for r in results:
        print(f"\n📸 {r['file']}")
        print(f"   → {r.get('result', r.get('error'))}")
```

## 第四步：Streamlit可视化界面

```python
# app.py
import streamlit as st
import openai
import base64

client = openai.OpenAI()

st.title("🔍 多模态AI图片分析器")
st.caption("上传图片，用AI理解任何视觉内容")

# 上传图片
uploaded = st.file_uploader("选择图片", type=["png", "jpg", "jpeg", "gif", "webp"])

# 预设任务
task = st.selectbox("选择任务", [
    "自由提问",
    "📄 OCR文字提取",
    "🧾 发票数据提取",
    "🏷️ 商品识别与定价",
    "📊 图表数据提取",
    "🎨 设计评审",
])

task_prompts = {
    "📄 OCR文字提取": "提取图片中所有可见的文字，保持原始格式。",
    "🧾 发票数据提取": "提取发票中的所有信息：商家、日期、商品、金额等。以结构化格式输出。",
    "🏷️ 商品识别与定价": "识别图片中的商品，估算市场价格范围，给出购买建议。",
    "📊 图表数据提取": "分析图表，提取数据点、趋势和关键发现。",
    "🎨 设计评审": "从UI/UX角度评审这个设计：布局、配色、可用性、改进建议。",
}

if task == "自由提问":
    question = st.text_input("你的问题", placeholder="这张图里有什么？")
else:
    question = task_prompts[task]
    st.info(f"提示词：{question}")

if uploaded and st.button("🚀 分析", type="primary"):
    image_data = base64.b64encode(uploaded.read()).decode()
    
    with st.spinner("AI正在分析..."):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": [
                {"type": "text", "text": question},
                {"type": "image_url", "image_url": {
                    "url": f"data:image/png;base64,{image_data}"
                }}
            ]}],
            max_tokens=1000
        )
    
    col1, col2 = st.columns(2)
    with col1:
        st.image(uploaded, caption="上传的图片")
    with col2:
        st.markdown("### 分析结果")
        st.write(response.choices[0].message.content)
        st.caption(f"模型: gpt-4o-mini | tokens: {response.usage.total_tokens}")
```

运行：
```bash
streamlit run app.py
```

## 成本分析

| 操作 | 模型 | 成本 |
|------|------|------|
| 单张图片分析 | gpt-4o-mini | ~$0.001 |
| 100张批量处理 | gpt-4o-mini | ~$0.10 |
| 复杂图片（高分辨率） | gpt-4o | ~$0.01 |
| 月均使用（1000张） | gpt-4o-mini | ~$1.00 |

**结论：多模态AI已经便宜到可以用在任何场景了。**

## 实战应用场景

1. **电商**：自动给商品图写描述、提取属性
2. **财务**：批量扫描发票/收据，自动记账
3. **内容审核**：检测不当内容
4. **医疗**：辅助分析医学影像（需专业验证）
5. **教育**：手写作业自动批改
6. **房产**：从房源照片提取特征

## 下一步

- 第四篇预告：**AI Agent——让AI自己决定调用什么工具**
- 完整代码：[GitHub仓库链接]

---

*觉得有用？关注 [@bitale14](https://x.com/bitale14) 获取更多AI实战教程。*
