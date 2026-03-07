# AI Agent with Tool Calling

A practical example of building an AI agent that can use tools to search the web, check weather, and execute Python code.

**Tutorial:** [Part 4: AI Agent](../../ai-agent-tutorial.md)

## Features

- 🌐 **Web Search** — Search the web using DuckDuckGo
- 🌦️ **Weather Data** — Get current weather for any city
- 🐍 **Code Execution** — Run Python code safely
- 🔗 **Tool Chaining** — Agent automatically chains multiple tools together
- 💬 **Interactive Mode** — Chat with the agent in terminal

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set API Key

```bash
export OPENAI_API_KEY=sk-your-key-here
```

### 3. Run the Agent

**Single query mode:**
```bash
python agent.py "What's the weather in Tokyo?"
python agent.py "Search for latest AI breakthroughs"
python agent.py "Calculate fibonacci(15)"
```

**Interactive mode:**
```bash
python agent.py interactive
```

**Verbose mode (see tool calls):**
```bash
python agent.py --verbose "What's the weather in London?"
```

## Example Queries

### Weather
```bash
python agent.py "What's the weather like in Paris right now?"
```

### Web Search
```bash
python agent.py "Search for the latest news about GPT-5"
```

### Code Execution
```bash
python agent.py "Calculate the 20th prime number"
python agent.py "Generate a random password with 16 characters"
```

### Multi-Tool Chaining
```bash
python agent.py "What's the weather in the capital of Japan?"
# Agent will: search "capital of Japan" → find "Tokyo" → get weather for Tokyo
```

## How It Works

### 1. Tool Definitions
The agent has access to 3 tools defined in JSON schema:
- `search_web(query)` — Web search via DuckDuckGo API
- `get_weather(city)` — Weather data via wttr.in API
- `run_python(code)` — Safe Python code execution

### 2. Agent Loop
```
User query → LLM decides which tool to use → Execute tool → Return result → LLM formulates answer
```

### 3. Tool Chaining Example
```
Query: "What's the weather in the capital of France?"

[Iteration 1] LLM calls search_web("capital of France")
→ Result: "Paris is the capital..."

[Iteration 2] LLM calls get_weather("Paris")
→ Result: "15°C, Partly Cloudy, Humidity: 68%"

[Iteration 3] LLM formulates final answer
→ "The weather in Paris is 15°C and partly cloudy with 68% humidity."
```

## Cost Estimate

Using `gpt-4o-mini`:
- **Single query:** $0.0001 - $0.0005 (depends on tool calls)
- **100 queries/day:** ~$0.02/day = $0.60/month

For production, consider:
- Rate limiting tool execution
- Caching search/weather results
- Using `gpt-3.5-turbo` for simpler queries

## Security Notes

### Code Execution Safety
The `run_python` tool has basic safeguards:
- ❌ Blocks `import os`, `import sys`, `exec`, `eval`, `open`
- ⏱️ 5-second timeout
- 🔒 Runs in subprocess (isolated from main process)

**NOT production-ready.** For production:
- Use sandboxed environments (Docker, Firecracker)
- Implement proper allowlists
- Add resource limits (CPU, memory, disk)

### API Keys
Never hardcode API keys. Use environment variables or `.env` files (add to `.gitignore`).

## Customization

### Add Your Own Tool
```python
# 1. Define the tool function
def get_stock_price(symbol: str) -> str:
    """Get current stock price."""
    # Your implementation here
    pass

# 2. Add tool definition to TOOLS list
{
    "type": "function",
    "function": {
        "name": "get_stock_price",
        "description": "Get current stock price for a symbol",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {"type": "string", "description": "Stock symbol (e.g., AAPL)"}
            },
            "required": ["symbol"]
        }
    }
}

# 3. Register in TOOL_FUNCTIONS
TOOL_FUNCTIONS = {
    "search_web": search_web,
    "get_weather": get_weather,
    "run_python": run_python,
    "get_stock_price": get_stock_price  # Add here
}
```

### Switch Model
```python
# Use GPT-4 for better reasoning (more expensive)
agent = Agent(model="gpt-4o")

# Use GPT-3.5 for cheaper queries
agent = Agent(model="gpt-3.5-turbo")
```

## Troubleshooting

### "OPENAI_API_KEY not set"
```bash
export OPENAI_API_KEY=sk-your-key-here
```

### "Module 'openai' not found"
```bash
pip install -r requirements.txt
```

### "Tool execution timeout"
The tool ran for >5 seconds. Either:
- Simplify the query
- Increase timeout in `run_python()`
- Check network connection (for web/weather tools)

### Agent gives wrong answer
- Try `gpt-4o` instead of `gpt-4o-mini` (better reasoning)
- Add `--verbose` to see which tools are being called
- Improve tool descriptions in `TOOLS` list

## Next Steps

1. **Add more tools** — Database queries, file operations, API calls
2. **Implement memory** — Store past interactions in a vector database
3. **Add streaming** — Stream LLM responses for better UX
4. **Deploy as API** — Wrap in FastAPI/Flask for production use
5. **Read Part 5** — [Multi-Agent Systems](../../multi-agent-system-tutorial.md)

## License

MIT — use this code however you want.

## Questions?

Open an issue or find me on [Twitter](https://x.com/bitale14).
