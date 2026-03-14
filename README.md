# AI Development Without a PhD

[![GitHub Stars](https://img.shields.io/github/stars/Alexhr414/ai-dev-no-phd?style=social)](https://github.com/Alexhr414/ai-dev-no-phd/stargazers)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

**6 production-ready AI tutorials — from zero to autonomous agents in one weekend.**

I spent months reading AI papers and getting nowhere. Then I just started building. This repo is everything I wish existed when I started.

> No PhD required. No math prerequisites. No $10,000 bootcamp. Just code that runs.

---

## ⚡ What You'll Build

| # | Tutorial | What You Learn | Code |
|---|----------|----------------|------|
| 1 | **AI Chatbot** | GPT-4 integration, conversation memory, system prompts | [📁 examples](./examples/) · [📖 tutorial](./ai-chatbot-tutorial.md) |
| 2 | **RAG System** | Vector search, knowledge retrieval, embeddings | [📁 examples](./examples/) · [📖 tutorial](./rag-chatbot-tutorial.md) |
| 3 | **Multimodal AI** | Text + image processing, vision models | [📖 tutorial](./multimodal-ai-tutorial.md) |
| 4 | **AI Agent** | Tool calling, function execution, autonomous decisions | [📖 tutorial](./ai-agent-tutorial.md) |
| 5 | **Multi-Agent System** | Agent orchestration, parallel workflows, handoffs | [📖 tutorial](./multi-agent-system-tutorial.md) |
| 6 | **MCP Server** | Connect Claude to any API, database, or tool | [📖 tutorial](./mcp-server-tutorial.md) |

---

## 🚀 Run Your First AI App in 5 Minutes

```bash
git clone https://github.com/Alexhr414/ai-dev-no-phd
cd ai-dev-no-phd/examples/part1-chatbot
pip install -r requirements.txt
OPENAI_API_KEY=your_key python chatbot.py
```

That's it. You're running a production-quality AI chatbot.

---

## 🎯 Who This Is For

- **Backend devs** adding AI to existing apps and not sure where to start
- **Indie hackers** building AI-powered tools that actually ship
- **Product engineers** prototyping AI features without reading research papers
- **Anyone** who learns by doing, not by watching 10-hour YouTube series

---

## 💡 What Makes This Different

Most AI tutorials show you a 50-line toy example and call it done.

This course covers:
- ✅ **Production patterns** — error handling, streaming, rate limits, cost optimization
- ✅ **Real use cases** — customer support bots, document search, autonomous agents
- ✅ **Decision frameworks** — when to use RAG vs fine-tuning vs prompting
- ✅ **Multi-provider** — examples work with OpenAI, Anthropic Claude, and local models
- ✅ **From basics to advanced** — linear path from Part 1 to Part 6, or jump in anywhere

---

## 📖 Course Structure

### Part 1: AI Chatbot
Build a chatbot with persistent memory, custom personality, and streaming responses. ~50 lines of code. Understand the OpenAI API from first principles.

### Part 2: RAG System  
Add a knowledge base your chatbot can search. Connect it to PDFs, docs, websites. Never hallucinate facts that are in your data again.

### Part 3: Multimodal AI
Go beyond text. Process images, generate descriptions, build visual Q&A systems. One API call.

### Part 4: AI Agent
Give your AI hands. Let it call APIs, execute code, search the web, take actions. This is where AI gets useful.

### Part 5: Multi-Agent System
Multiple AIs working together. Researcher + Analyst + Writer agents that collaborate automatically. The architecture behind most AI products you've heard of.

### Part 6: MCP Server
Build a Model Context Protocol server. Connect Claude Desktop to your own tools, databases, and APIs. The new standard for AI tool integration.

---

## 🛠 Tech Stack

```
Python 3.9+
OpenAI API (GPT-4, embeddings, vision)
ChromaDB (vector database)
OpenAI Swarm (multi-agent)
Anthropic MCP SDK
```

---

## 🤝 Contributing

Found a bug? Have a better approach? PRs welcome.

- Fix typos, improve explanations
- Add examples for other LLM providers (Anthropic, Gemini, Ollama)
- Translate tutorials to other languages
- Add production deployment guides (Docker, Railway, Fly.io)

---

## ⭐ Support This Project

If this helped you ship something, consider:

- **Star this repo** — helps other developers find it
- **[GitHub Sponsors](https://github.com/sponsors/Alexhr414)** — support ongoing tutorials
- **Share with a friend** who's trying to learn AI without the academic overhead

---

## 📬 Questions?

Open an issue. I reply to all of them.

---

*Built by a developer who got tired of AI tutorials that never shipped.*
