# AI Development Without a PhD (Part 5): Multi-Agent Systems with OpenAI Swarm

*This is Part 5 of the "AI Development Without a PhD" series. Check out [Part 1 (Chatbot)](./ai-chatbot-tutorial.md), [Part 2 (RAG)](./rag-chatbot-tutorial.md), [Part 3 (Multimodal)](./multimodal-ai-tutorial.md), and [Part 4 (AI Agent)](./ai-agent-tutorial.md) if you haven't yet.*

---

## What You'll Learn

In Part 4, we built an AI agent that could call tools autonomously. But real-world tasks often need **multiple agents collaborating** — one to research, another to write, a third to review.

In this tutorial, you'll build a **multi-agent system** where:
- **Researcher Agent** searches the web for information
- **Writer Agent** synthesizes findings into a structured report
- **Coordinator Agent** orchestrates the handoffs

We'll use **OpenAI Swarm**, a lightweight framework for agent coordination via function-based handoffs.

---

## Prerequisites

- Python 3.9+
- OpenAI API key
- Basic understanding of function calling (from Part 4)

---

## 1. Setup

### Install Dependencies

```bash
pip install openai git+https://github.com/openai/swarm.git
```

### Environment

Create `.env`:
```
OPENAI_API_KEY=your_key_here
```

---

## 2. What is Multi-Agent Orchestration?

Instead of one agent handling everything, you split the work:

```
User Request → Coordinator → Researcher → Writer → Final Output
```

Each agent has:
- **Role**: Specialized instructions (e.g., "You are a web researcher")
- **Tools**: Functions it can call (e.g., `web_search()`)
- **Handoff Functions**: Transfer control to another agent

---

## 3. Define Agents

### Base Agent Structure (Swarm Style)

```python
from swarm import Agent

researcher = Agent(
    name="Researcher",
    instructions="You search the web for factual information. Be concise.",
    functions=[web_search, handoff_to_writer]
)

writer = Agent(
    name="Writer",
    instructions="You synthesize research into structured reports.",
    functions=[handoff_to_coordinator]
)

coordinator = Agent(
    name="Coordinator",
    instructions="You orchestrate the workflow. Start by handing off to Researcher.",
    functions=[handoff_to_researcher]
)
```

---

## 4. Implement Tools

### Web Search Tool

```python
import requests

def web_search(query: str) -> str:
    """Search the web and return top results."""
    # Example using DuckDuckGo Instant Answer API (no auth needed)
    url = f"https://api.duckduckgo.com/?q={query}&format=json"
    response = requests.get(url)
    data = response.json()
    
    if data.get('AbstractText'):
        return f"Found: {data['AbstractText']}"
    else:
        return f"No direct answer. Related topics: {data.get('RelatedTopics', [])[:3]}"
```

### Handoff Functions

```python
def handoff_to_researcher():
    """Transfer control to Researcher agent."""
    return researcher

def handoff_to_writer():
    """Transfer control to Writer agent."""
    return writer

def handoff_to_coordinator():
    """Return to Coordinator."""
    return coordinator
```

---

## 5. Run the Multi-Agent Workflow

```python
from swarm import Swarm

client = Swarm()

# Start with Coordinator
response = client.run(
    agent=coordinator,
    messages=[{"role": "user", "content": "Research the impact of AI on employment and write a summary."}]
)

print(response.messages[-1]["content"])
```

### Execution Flow

1. **User → Coordinator**: "Research AI and employment"
2. **Coordinator → Researcher**: Calls `handoff_to_researcher()`
3. **Researcher**: Calls `web_search("AI impact on employment")`, returns results
4. **Researcher → Writer**: Calls `handoff_to_writer()`
5. **Writer**: Synthesizes findings into a report
6. **Writer → Coordinator**: Calls `handoff_to_coordinator()`
7. **Coordinator**: Returns final output to user

---

## 6. Advanced: Dynamic Routing

Instead of fixed handoffs, let the Coordinator **decide** which agent to call based on the task:

```python
coordinator = Agent(
    name="Coordinator",
    instructions="""
    You are a task router. Based on the user's request:
    - If it needs data, hand off to Researcher
    - If it needs writing, hand off to Writer
    - If it's simple, answer directly
    """,
    functions=[handoff_to_researcher, handoff_to_writer]
)
```

Now the workflow adapts: "Explain quantum computing" might skip research if the model already knows enough.

---

## 7. Full Code Example

```python
from swarm import Swarm, Agent
import requests

def web_search(query: str) -> str:
    url = f"https://api.duckduckgo.com/?q={query}&format=json"
    response = requests.get(url)
    data = response.json()
    return data.get('AbstractText', 'No results')

def handoff_to_researcher():
    return researcher

def handoff_to_writer():
    return writer

def handoff_to_coordinator():
    return coordinator

researcher = Agent(
    name="Researcher",
    instructions="Search the web and provide factual data.",
    functions=[web_search, handoff_to_writer]
)

writer = Agent(
    name="Writer",
    instructions="Synthesize research into clear summaries.",
    functions=[handoff_to_coordinator]
)

coordinator = Agent(
    name="Coordinator",
    instructions="Orchestrate multi-step tasks. Start with Researcher.",
    functions=[handoff_to_researcher]
)

client = Swarm()
response = client.run(
    agent=coordinator,
    messages=[{"role": "user", "content": "Research renewable energy trends and summarize."}]
)

print(response.messages[-1]["content"])
```

---

## 8. When to Use Multi-Agent Systems

✅ **Good for:**
- Complex workflows (research → write → review)
- Specialized expertise per agent
- Parallel tasks (e.g., multiple researchers)

❌ **Overkill for:**
- Simple Q&A (use single agent from Part 4)
- Linear tool chains (just call tools sequentially)

---

## 9. Comparing Frameworks

| Framework | Best For | Complexity |
|-----------|----------|-----------|
| **Swarm** | Lightweight handoffs, learning | Low |
| **CrewAI** | Role-playing teams (e.g., CEO + CTO) | Medium |
| **LangGraph** | Stateful workflows, loops | High |
| **AutoGen** | Conversational multi-agent | High |

Start with **Swarm** for prototyping. Upgrade to LangGraph/CrewAI for production.

---

## 10. Next Steps

- **Add Memory**: Store conversation context between agents (see LangGraph docs)
- **Parallel Agents**: Run multiple researchers simultaneously
- **Human-in-the-Loop**: Add approval steps before agent handoffs

Want to go deeper? Check out:
- [OpenAI Swarm GitHub](https://github.com/openai/swarm)
- [LangGraph Multi-Agent Guide](https://docs.langchain.com/oss/python/langchain/multi-agent)
- [CrewAI Quickstart](https://docs.crewai.com/en/introduction)

---

## Series Recap

You've now built:
1. **Chatbot** (Part 1) — Basic Q&A
2. **RAG System** (Part 2) — Knowledge retrieval
3. **Multimodal Agent** (Part 3) — Text + images
4. **AI Agent** (Part 4) — Tool-calling autonomy
5. **Multi-Agent System** (Part 5) — Collaborative workflows

**You know enough to build production-grade AI apps.** The rest is just scaling, optimization, and domain expertise.

---

## About This Series

This is part of the **"AI Development Without a PhD"** course — practical, no-fluff tutorials for developers who want to ship AI apps fast.

- Full code examples
- Real-world use cases
- No academic jargon

**Want the complete course?** [Get it here](#) (launch special: $9, regular $19)

---

*Questions? Find me on [Twitter](#) or [GitHub](#).*
