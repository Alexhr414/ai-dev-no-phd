# AI Development Without a PhD

**Practical tutorials for building AI apps — no academic background required.**

This is a hands-on course for developers who want to ship production-grade AI systems fast. No theory fluff. No math prerequisites. Just working code and real-world patterns.

---

## What You'll Build

| Tutorial | What You Learn | Link |
|----------|----------------|------|
| **Part 1: AI Chatbot** | Build a basic Q&A bot with OpenAI API | [Read](./ai-chatbot-tutorial.md) |
| **Part 2: RAG System** | Add knowledge retrieval with vector search | [Read](./rag-chatbot-tutorial.md) |
| **Part 3: Multimodal AI** | Process text + images with vision models | [Read](./multimodal-ai-tutorial.md) |
| **Part 4: AI Agent** | Enable tool calling and autonomous actions | [Read](./ai-agent-tutorial.md) |
| **Part 5: Multi-Agent System** | Orchestrate collaborative agent workflows | [Read](./multi-agent-system-tutorial.md) |

---

## Who This Is For

- **Backend developers** adding AI to existing apps
- **Product engineers** prototyping AI features
- **Indie hackers** building AI-powered tools
- **Anyone** tired of academic AI papers and ready to build

---

## What You'll Know After This Course

✅ How to integrate LLMs into production apps  
✅ When to use RAG vs fine-tuning vs prompting  
✅ How to build autonomous agents that call APIs  
✅ How to orchestrate multi-agent workflows  
✅ Real-world cost/latency tradeoffs  

**You'll have enough knowledge to build and ship AI apps on day one.**

---

## Tech Stack

- **Python 3.9+** (all examples are in Python)
- **OpenAI API** (GPT-4, embeddings, vision)
- **ChromaDB** (vector database for RAG)
- **OpenAI Swarm** (multi-agent orchestration)

Most examples work with other LLM providers (Anthropic, Gemini, local models) with minimal changes.

---

## How to Use This Course

1. **Sequential**: Start with Part 1, build progressively (recommended for beginners)
2. **Jump-in**: Go straight to the tutorial matching your goal (if you know the basics)

Each tutorial includes:
- Full code examples
- Step-by-step explanations
- Production considerations (cost, latency, security)

---

## Getting Started

### Prerequisites

```bash
# Install Python 3.9+
python3 --version

# Install OpenAI SDK
pip install openai

# Set API key
export OPENAI_API_KEY="your_key_here"
```

### Run Your First Chatbot (5 minutes)

```python
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Explain AI in one sentence."}]
)

print(response.choices[0].message.content)
```

**Output**: "AI is software that learns patterns from data to make predictions or decisions without explicit programming."

👉 **Now go to [Part 1](./ai-chatbot-tutorial.md) for the full tutorial.**

---

## Course Philosophy

### ❌ What This Isn't

- Not a research paper anthology
- Not a math/stats bootcamp
- Not a "here's a framework, figure it out" guide

### ✅ What This Is

- **Working code first**: Every concept comes with runnable examples
- **Production-ready patterns**: Real error handling, cost optimization, security
- **Progressive complexity**: Start simple, add layers incrementally

If you can write a `for` loop, you can build AI apps. The rest is just API calls and patterns.

---

## Why This Course Exists

Most AI tutorials fall into two camps:
1. **Academic**: Heavy on theory, light on code
2. **Framework docs**: "Here's our tool, good luck"

This course is the middle ground: **enough theory to make informed decisions, enough code to ship products.**

Built by developers, for developers.

---

## Repository Structure

```
ai-dev-no-phd/
├── README.md                       # You are here
├── ai-chatbot-tutorial.md          # Part 1
├── rag-chatbot-tutorial.md         # Part 2
├── multimodal-ai-tutorial.md       # Part 3
├── ai-agent-tutorial.md            # Part 4
├── multi-agent-system-tutorial.md  # Part 5
└── examples/                       # Full code samples (coming soon)
```

---

## Contributing

Found a bug? Have a suggestion? Open an issue or PR.

This course is open-source because AI development should be accessible to everyone.

---

## License

MIT License — use the code however you want.

---

## About the Author

Built by [@bitale14](https://x.com/bitale14) — sharing what I learn while building AI systems in the real world.

**Questions?** Find me on [Twitter](https://x.com/bitale14) or open a GitHub issue.

---

## Support This Project

If these tutorials saved you 100 hours of trial-and-error, consider [buying me a coffee ☕](https://github.com/sponsors/Alexhr414).

Writing comprehensive tutorials takes time — your support helps me create more content like this.

---

## Next Steps

1. **Start with [Part 1](./ai-chatbot-tutorial.md)** if you're new to AI development
2. **Star this repo** to follow updates
3. **Share with other developers** who want to learn AI without the academic overhead

Let's build. 🚀
