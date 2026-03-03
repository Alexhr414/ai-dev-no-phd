# Build an AI Agent That Actually Does Things (Tool Calling from Scratch)

*Your AI chatbot can talk. Cool. Now let's make it DO stuff — search the web, check the weather, run code, query databases. This is how real AI agents work.*

---

## Why This Tutorial?

ChatGPT can chat. But the AI apps making real money in 2026? They **act**. They book flights, analyze spreadsheets, monitor servers, and write code. The secret sauce? **Tool calling** — giving your AI the ability to use functions like a developer uses APIs.

This is Part 4 of our AI development series:
1. [AI Chatbot](./ai-chatbot-tutorial.md) — conversation basics
2. [RAG Chatbot](./rag-chatbot-tutorial.md) — knowledge retrieval
3. [Multimodal AI](./multimodal-ai-tutorial.md) — vision & images
4. **AI Agent** (this one) — tool calling & autonomous action

## What You'll Build

An AI agent that can:
- ✅ Search the web for real-time information
- ✅ Get current weather for any city
- ✅ Execute Python code and return results
- ✅ Chain multiple tools together automatically
- ✅ Decide *which* tool to use based on your question

No frameworks. No LangChain. Just Python + OpenAI API + clear understanding.

## Prerequisites

- Python 3.10+
- OpenAI API key (from previous tutorials)
- 45 minutes of focus
- Completed Part 1 (helpful but not required)

---

## The Big Idea: What IS Tool Calling?

Normal chatbot:
```
You: "What's the weather in Tokyo?"
AI: "I don't have real-time data, but Tokyo typically..."  ← USELESS
```

AI Agent with tools:
```
You: "What's the weather in Tokyo?"
AI: [thinks] I should use the weather tool → calls get_weather("Tokyo")
Tool returns: {"temp": 12, "condition": "cloudy", "humidity": 65}
AI: "It's 12°C and cloudy in Tokyo right now, with 65% humidity."  ← ACTUALLY USEFUL
```

The AI doesn't magically know the weather. It **decides** to call a function, gets real data back, and formulates a response. That's the entire concept.

## Step 1: Project Setup

```bash
mkdir ai-agent && cd ai-agent
python -m venv venv && source venv/bin/activate
pip install openai requests python-dotenv
```

Create `.env`:
```
OPENAI_API_KEY=sk-your-key-here
```

## Step 2: Define Your Tools

Tools are just Python functions with a specific JSON description that tells the AI what they do.

Create `tools.py`:

```python
import requests
import subprocess
import json

def search_web(query: str) -> str:
    """Search the web using DuckDuckGo Instant Answer API."""
    resp = requests.get(
        "https://api.duckduckgo.com/",
        params={"q": query, "format": "json", "no_html": 1}
    )
    data = resp.json()
    
    # Try abstract first (Wikipedia-style answer)
    if data.get("Abstract"):
        return f"**{data['Heading']}**\n{data['Abstract']}\nSource: {data['AbstractURL']}"
    
    # Fall back to related topics
    topics = data.get("RelatedTopics", [])[:3]
    if topics:
        results = []
        for t in topics:
            if isinstance(t, dict) and "Text" in t:
                results.append(t["Text"])
        return "\n".join(results) if results else "No results found."
    
    return "No results found for this query."


def get_weather(city: str) -> str:
    """Get current weather for a city using wttr.in."""
    resp = requests.get(
        f"https://wttr.in/{city}",
        params={"format": "j1"},
        timeout=10
    )
    data = resp.json()
    current = data["current_condition"][0]
    
    return json.dumps({
        "city": city,
        "temperature_c": current["temp_C"],
        "feels_like_c": current["FeelsLikeC"],
        "condition": current["weatherDesc"][0]["value"],
        "humidity": current["humidity"] + "%",
        "wind_kmh": current["windspeedKmph"]
    }, indent=2)


def run_python(code: str) -> str:
    """Execute Python code and return the output."""
    try:
        result = subprocess.run(
            ["python", "-c", code],
            capture_output=True,
            text=True,
            timeout=10
        )
        output = result.stdout.strip()
        if result.returncode != 0:
            output = f"Error: {result.stderr.strip()}"
        return output if output else "Code executed successfully (no output)."
    except subprocess.TimeoutExpired:
        return "Error: Code execution timed out (10s limit)."


def calculate(expression: str) -> str:
    """Safely evaluate a mathematical expression."""
    # Only allow safe math operations
    allowed = set("0123456789+-*/.() ")
    if not all(c in allowed for c in expression):
        return "Error: Only basic math operations allowed."
    try:
        result = eval(expression)  # Safe because we validated input
        return str(result)
    except Exception as e:
        return f"Error: {e}"


# Registry: maps function names to actual functions
TOOL_FUNCTIONS = {
    "search_web": search_web,
    "get_weather": get_weather,
    "run_python": run_python,
    "calculate": calculate,
}

# OpenAI tool definitions (JSON Schema)
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the web for current information on any topic. Use this when the user asks about facts, people, events, or anything that requires up-to-date knowledge.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather conditions for a city. Use when the user asks about weather, temperature, or conditions in a specific location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name (e.g., 'Tokyo', 'New York', 'London')"
                    }
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_python",
            "description": "Execute Python code and return the output. Use for calculations, data processing, or any task that benefits from running code.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python code to execute"
                    }
                },
                "required": ["code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluate a mathematical expression. Use for simple arithmetic.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Math expression (e.g., '2 + 2', '100 * 1.08')"
                    }
                },
                "required": ["expression"]
            }
        }
    },
]
```

Notice the pattern: each tool is just a function + a JSON description. The AI reads the descriptions to decide when to use what.

## Step 3: The Agent Loop

This is where the magic happens. The "agent loop" is simple:

1. Send message + tool definitions to the AI
2. If the AI wants to call a tool → execute it → send results back
3. Repeat until the AI gives a final text response

Create `agent.py`:

```python
import json
import os
from openai import OpenAI
from dotenv import load_dotenv
from tools import TOOL_FUNCTIONS, TOOL_DEFINITIONS

load_dotenv()
client = OpenAI()

SYSTEM_PROMPT = """You are a helpful AI assistant with access to tools.
Use tools when they would help answer the user's question accurately.
You can chain multiple tools if needed.
Always be direct and concise in your responses."""


def run_agent(user_message: str, conversation: list = None) -> str:
    """Run the agent loop: message → tool calls → response."""
    
    if conversation is None:
        conversation = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    conversation.append({"role": "user", "content": user_message})
    
    # Agent loop — max 5 iterations to prevent infinite loops
    for i in range(5):
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Cheap and great at tool calling
            messages=conversation,
            tools=TOOL_DEFINITIONS,
            tool_choice="auto",  # Let the AI decide
        )
        
        message = response.choices[0].message
        conversation.append(message)
        
        # If no tool calls, we have our final answer
        if not message.tool_calls:
            return message.content
        
        # Execute each tool call
        print(f"  🔧 Agent is using {len(message.tool_calls)} tool(s)...")
        
        for tool_call in message.tool_calls:
            func_name = tool_call.function.name
            func_args = json.loads(tool_call.function.arguments)
            
            print(f"  → {func_name}({func_args})")
            
            # Call the actual function
            func = TOOL_FUNCTIONS.get(func_name)
            if func:
                result = func(**func_args)
            else:
                result = f"Error: Unknown tool '{func_name}'"
            
            # Send the result back to the AI
            conversation.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })
    
    return "Agent reached maximum iterations without a final response."


# Interactive mode
if __name__ == "__main__":
    print("🤖 AI Agent ready! (type 'quit' to exit)\n")
    conversation = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            break
        if not user_input:
            continue
        
        response = run_agent(user_input, conversation)
        print(f"\nAgent: {response}\n")
```

## Step 4: Try It Out

```bash
python agent.py
```

```
🤖 AI Agent ready! (type 'quit' to exit)

You: What's the weather in Tokyo and convert the temperature to Fahrenheit?
  🔧 Agent is using 2 tool(s)...
  → get_weather({"city": "Tokyo"})
  → calculate({"expression": "12 * 9/5 + 32"})

Agent: It's currently 12°C (53.6°F) and cloudy in Tokyo, with 65% humidity 
       and winds at 15 km/h.

You: Write a Python script that finds all prime numbers under 100
  🔧 Agent is using 1 tool(s)...
  → run_python({"code": "primes = [n for n in range(2, 100) if all(n%i for i in range(2, int(n**0.5)+1))]\nprint(primes)"})

Agent: Here are all 25 prime numbers under 100:
       [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 
        53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
```

**That's it.** Your AI can now *do things*. No LangChain. No framework. Just clean Python.

## Step 5: Add a Web Interface

Let's make it pretty. Create `app.py`:

```python
from flask import Flask, render_template_string, request, jsonify
from agent import run_agent

app = Flask(__name__)
conversations = {}

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Agent</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif;
               background: #0a0a0a; color: #e0e0e0; height: 100vh;
               display: flex; flex-direction: column; }
        #chat { flex: 1; overflow-y: auto; padding: 20px; }
        .msg { max-width: 80%; margin: 8px 0; padding: 12px 16px;
               border-radius: 12px; line-height: 1.5; }
        .user { background: #1a73e8; color: white; margin-left: auto; }
        .agent { background: #1e1e1e; border: 1px solid #333; }
        .tool { background: #1a1a2e; border: 1px solid #2a2a4e; 
                font-size: 0.85em; font-family: monospace; }
        #input-area { display: flex; padding: 16px; gap: 8px;
                      border-top: 1px solid #222; }
        input { flex: 1; padding: 12px; border-radius: 8px;
                border: 1px solid #333; background: #1e1e1e; 
                color: white; font-size: 16px; }
        button { padding: 12px 24px; border-radius: 8px; border: none;
                 background: #1a73e8; color: white; cursor: pointer;
                 font-size: 16px; }
        button:hover { background: #1557b0; }
    </style>
</head>
<body>
    <div id="chat"></div>
    <div id="input-area">
        <input id="msg" placeholder="Ask anything..." 
               onkeypress="if(event.key==='Enter')send()">
        <button onclick="send()">Send</button>
    </div>
    <script>
        async function send() {
            const input = document.getElementById('msg');
            const msg = input.value.trim();
            if (!msg) return;
            
            addMsg(msg, 'user');
            input.value = '';
            
            const resp = await fetch('/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: msg})
            });
            const data = await resp.json();
            
            if (data.tools) {
                data.tools.forEach(t => addMsg(`🔧 ${t}`, 'tool'));
            }
            addMsg(data.response, 'agent');
        }
        
        function addMsg(text, cls) {
            const chat = document.getElementById('chat');
            const div = document.createElement('div');
            div.className = 'msg ' + cls;
            div.textContent = text;
            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/chat', methods=['POST'])
def chat():
    msg = request.json['message']
    session_id = request.remote_addr
    
    if session_id not in conversations:
        conversations[session_id] = [
            {"role": "system", "content": "You are a helpful AI agent with tools."}
        ]
    
    response = run_agent(msg, conversations[session_id])
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
```

```bash
pip install flask
python app.py
```

Open `http://localhost:5001` — you've got a web-based AI agent.

## Step 6: Make It Smarter — Tool Chaining

The real power comes when the agent chains tools. It already does this automatically:

```
You: "What's the population of the 3 biggest cities in Japan, 
      and calculate their total?"

Agent thinking:
  1. search_web("largest cities Japan population")
  2. calculate("13960000 + 3750000 + 2750000")
  → "The three largest cities in Japan are Tokyo (13.96M), 
     Osaka (3.75M), and Yokohama (2.75M), with a combined 
     population of 20.46 million."
```

No extra code needed. The agent loop handles iteration naturally.

## How It Actually Works (Under the Hood)

```
┌─────────┐     ┌──────────┐     ┌─────────┐
│  User    │────▶│  OpenAI  │────▶│  Tools  │
│  Message │     │   API    │     │(Python) │
└─────────┘     └──────────┘     └─────────┘
                     │                 │
                     │  "call weather" │
                     │────────────────▶│
                     │                 │
                     │  {temp: 12}     │
                     │◀────────────────│
                     │                 │
                     │  Final answer   │
                     │────────────────▶│ User
```

1. Your message + tool schemas go to OpenAI
2. The model returns either text OR tool calls (structured JSON)
3. You execute the functions locally (OpenAI never runs your code)
4. Results go back as `tool` messages
5. The model incorporates results into its final response

**Key insight**: The AI model never executes tools. It only *requests* them. You control what actually runs. This is why it's safe — you decide which functions exist and what they can access.

## Adding Your Own Tools

Want to add a new tool? Three steps:

1. **Write the function** in `tools.py`
2. **Add the JSON schema** to `TOOL_DEFINITIONS`
3. **Register it** in `TOOL_FUNCTIONS`

Example — a tool that checks if a website is up:

```python
def check_website(url: str) -> str:
    """Check if a website is responding."""
    try:
        resp = requests.get(url, timeout=5)
        return json.dumps({
            "url": url,
            "status": resp.status_code,
            "response_time_ms": round(resp.elapsed.total_seconds() * 1000),
            "is_up": resp.status_code < 400
        })
    except Exception as e:
        return json.dumps({"url": url, "is_up": False, "error": str(e)})
```

Add the schema, register it, done. Your agent can now monitor websites.

## What's Next?

You now have the building blocks of every AI agent:
- **Memory** (conversation history from Part 1)
- **Knowledge** (RAG from Part 2)
- **Vision** (multimodal from Part 3)
- **Action** (tool calling from this tutorial)

Combine all four and you can build:
- 📊 Data analysis agents that read CSVs, run stats, and generate reports
- 🛒 Shopping assistants that search products and compare prices
- 📝 Research agents that search, summarize, and cite sources
- 🔧 DevOps bots that monitor servers, check logs, and restart services

## Full Code

All code from this tutorial: [GitHub repo link]

---

*This is Part 4 of the "AI Development Without a PhD" series. [Subscribe](#) for Part 5: Building a Multi-Agent System.*

**Estimated reading time:** 15 minutes  
**Difficulty:** Intermediate  
**Cost to run:** ~$0.01-0.05 per conversation (gpt-4o-mini)
