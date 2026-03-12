# Build Your Own MCP Server: Connect Claude to Anything

*Everyone's talking about MCP (Model Context Protocol). Here's how to actually build one — a server that lets Claude read your files, query your database, or call any API you own.*

---

## Why MCP?

In 2026, the AI apps that win aren't just "chat with GPT." They're **context-aware** — they can reach into your Notion, your database, your custom APIs. MCP is Anthropic's open protocol that makes this possible without writing glue code forever.

Think of MCP as **USB-C for AI**: a standard port that any LLM host can plug into.

This is Part 6 of the AI Development Without a PhD series:
1. [AI Chatbot](./ai-chatbot-tutorial.md) — conversation basics  
2. [RAG Chatbot](./rag-chatbot-tutorial.md) — knowledge retrieval  
3. [Multimodal AI](./multimodal-ai-tutorial.md) — vision & images  
4. [AI Agent](./ai-agent-tutorial.md) — tool calling  
5. [Multi-Agent System](./multi-agent-system-tutorial.md) — coordination  
6. **MCP Server** (this one) — custom integrations

## What You'll Build

A working MCP server that:
- ✅ Exposes custom **tools** Claude can call
- ✅ Provides **resources** (files, data) Claude can read
- ✅ Connects to a real SQLite database
- ✅ Works with Claude Desktop in 10 minutes

No prior MCP experience needed. Just Python.

## Prerequisites

- Python 3.10+
- `pip install mcp anthropic`
- Claude Desktop (free): https://claude.ai/download

---

## Part 1: What Even Is MCP?

When you use Claude in Claude Desktop, it can access your filesystem, run searches, and read files — that's all powered by MCP servers running on your machine.

The architecture:

```
Claude Desktop (MCP Host)
    ↕ JSON-RPC over stdio
Your MCP Server (Python)
    ↕ Python code
Your Data / APIs / Database
```

Your MCP server exposes two things:
1. **Tools** — functions Claude can call ("run this query", "fetch this URL")
2. **Resources** — read-only data Claude can access ("show me this file", "fetch this config")

---

## Part 2: Your First MCP Server (5 minutes)

```python
# server.py
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types
import asyncio

# Create server instance
app = Server("my-first-mcp")

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    """Tell Claude what tools are available."""
    return [
        types.Tool(
            name="get_time",
            description="Returns the current date and time",
            inputSchema={
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "Timezone like 'UTC' or 'Europe/Brussels'",
                        "default": "UTC"
                    }
                }
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Execute the tool Claude requested."""
    if name == "get_time":
        from datetime import datetime
        import zoneinfo
        
        tz_name = arguments.get("timezone", "UTC")
        try:
            tz = zoneinfo.ZoneInfo(tz_name)
        except Exception:
            tz = zoneinfo.ZoneInfo("UTC")
        
        now = datetime.now(tz)
        result = f"Current time in {tz_name}: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}"
        
        return [types.TextContent(type="text", text=result)]
    
    return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
```

That's a complete MCP server. Let's connect it to Claude Desktop.

---

## Part 3: Connect to Claude Desktop

Find your Claude Desktop config:
- **Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

Add your server:

```json
{
  "mcpServers": {
    "my-first-mcp": {
      "command": "python",
      "args": ["/absolute/path/to/server.py"]
    }
  }
}
```

Restart Claude Desktop. You should see a 🔧 icon indicating tools are available.

Try asking: *"What time is it in Tokyo?"*

---

## Part 4: Add Resources (Read-Only Data)

Resources let Claude access your data without you manually pasting it.

```python
@app.list_resources()
async def list_resources() -> list[types.Resource]:
    """Expose files/data Claude can read."""
    return [
        types.Resource(
            uri="file://config/settings",
            name="App Settings",
            description="Current application configuration",
            mimeType="application/json"
        )
    ]

@app.read_resource()
async def read_resource(uri: str) -> str:
    """Return the content of a requested resource."""
    if uri == "file://config/settings":
        import json
        config = {
            "version": "1.0",
            "environment": "production",
            "features": ["rag", "agents", "mcp"]
        }
        return json.dumps(config, indent=2)
    
    raise ValueError(f"Resource not found: {uri}")
```

Now Claude can ask for your settings when it needs them.

---

## Part 5: Real Example — Database Query Tool

Here's a practical MCP server with SQLite access:

```python
# database_server.py
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types
import asyncio
import sqlite3
import json

app = Server("database-mcp")

# Create sample database
def init_db():
    conn = sqlite3.connect("demo.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    """)
    # Sample data
    conn.execute("DELETE FROM products")
    products = [
        ("Laptop", 999.99, 50),
        ("Mouse", 29.99, 200),
        ("Keyboard", 79.99, 150),
        ("Monitor", 349.99, 30),
        ("Headphones", 149.99, 75),
    ]
    conn.executemany("INSERT INTO products (name, price, stock) VALUES (?, ?, ?)", products)
    conn.commit()
    conn.close()

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="query_database",
            description="Run a SQL SELECT query on the products database",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SQL SELECT query to execute"
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="get_low_stock",
            description="Get products with stock below a threshold",
            inputSchema={
                "type": "object",
                "properties": {
                    "threshold": {
                        "type": "integer",
                        "description": "Minimum stock level (default: 50)",
                        "default": 50
                    }
                }
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    conn = sqlite3.connect("demo.db")
    conn.row_factory = sqlite3.Row
    
    try:
        if name == "query_database":
            query = arguments["query"]
            
            # Safety: only allow SELECT
            if not query.strip().upper().startswith("SELECT"):
                return [types.TextContent(
                    type="text", 
                    text="Error: Only SELECT queries are allowed"
                )]
            
            cursor = conn.execute(query)
            rows = [dict(row) for row in cursor.fetchall()]
            
            if not rows:
                return [types.TextContent(type="text", text="No results found")]
            
            # Format as table
            result = f"Found {len(rows)} rows:\n\n"
            result += json.dumps(rows, indent=2)
            return [types.TextContent(type="text", text=result)]
        
        elif name == "get_low_stock":
            threshold = arguments.get("threshold", 50)
            cursor = conn.execute(
                "SELECT name, stock, price FROM products WHERE stock < ? ORDER BY stock ASC",
                (threshold,)
            )
            rows = [dict(row) for row in cursor.fetchall()]
            
            if not rows:
                return [types.TextContent(
                    type="text", 
                    text=f"All products have stock above {threshold}"
                )]
            
            result = f"⚠️ {len(rows)} products with stock below {threshold}:\n\n"
            for row in rows:
                result += f"• {row['name']}: {row['stock']} units (${row['price']})\n"
            return [types.TextContent(type="text", text=result)]
    
    finally:
        conn.close()
    
    return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

async def main():
    init_db()
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
```

Install and run:
```bash
pip install mcp
python database_server.py
```

Add to Claude Desktop config, then ask:
- *"Which products are running low on stock?"*
- *"What's our most expensive product?"*
- *"Show me all products under $100"*

Claude will use your tools to answer — no copy-pasting data required.

---

## Part 6: Production Patterns

### Pattern 1: Environment Variables for Secrets

Never hardcode API keys in your MCP server:

```python
import os

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///demo.db")
API_KEY = os.environ.get("SOME_API_KEY")

if not API_KEY:
    raise ValueError("SOME_API_KEY environment variable required")
```

In Claude Desktop config:
```json
{
  "mcpServers": {
    "my-server": {
      "command": "python",
      "args": ["/path/to/server.py"],
      "env": {
        "SOME_API_KEY": "your-key-here",
        "DATABASE_URL": "postgresql://..."
      }
    }
  }
}
```

### Pattern 2: Error Handling That Helps Claude

```python
@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    try:
        # Your tool logic
        result = do_something(arguments)
        return [types.TextContent(type="text", text=result)]
    
    except KeyError as e:
        # Missing required argument — Claude can retry with correct args
        return [types.TextContent(
            type="text",
            text=f"Missing required argument: {e}. Please provide it."
        )]
    except ConnectionError as e:
        # External service down — Claude should inform user
        return [types.TextContent(
            type="text",
            text=f"Could not connect to service: {e}. Try again later."
        )]
    except Exception as e:
        # Generic fallback
        return [types.TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]
```

### Pattern 3: Async External API Calls

```python
import httpx

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "fetch_weather":
        city = arguments["city"]
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://wttr.in/{city}",
                params={"format": "j1"},
                timeout=10.0
            )
            data = response.json()
            
            temp = data["current_condition"][0]["temp_C"]
            desc = data["current_condition"][0]["weatherDesc"][0]["value"]
            
            return [types.TextContent(
                type="text",
                text=f"{city}: {temp}°C, {desc}"
            )]
```

---

## Part 7: Testing Your MCP Server

Don't just test in Claude Desktop. Use the MCP inspector:

```bash
pip install mcp[cli]
mcp dev server.py
```

This opens an interactive web UI where you can:
- List all tools and resources
- Call tools manually with test arguments
- See exact JSON-RPC messages

---

## What's Next?

You now know how to:
- ✅ Build MCP servers with tools and resources
- ✅ Connect them to Claude Desktop
- ✅ Query databases safely
- ✅ Handle errors properly
- ✅ Use environment variables for secrets

**Ideas to build:**
- Connect your Notion workspace
- Query your PostgreSQL database
- Fetch data from internal APIs
- Read local files and documents
- Integrate with Slack, GitHub, or Linear

The complete code for this tutorial is in the `examples/` folder of this repo.

⭐ **If this saved you time, [star the repo](https://github.com/Alexhr414/ai-dev-no-phd)** — it helps more developers find these tutorials.

---

*Part of the [AI Development Without a PhD](https://github.com/Alexhr414/ai-dev-no-phd) series. MIT licensed. No PhD required.*
