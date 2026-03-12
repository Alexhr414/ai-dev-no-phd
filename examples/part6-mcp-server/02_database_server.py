"""
Part 6: MCP Server Tutorial - Example 2
Database MCP Server - Connect Claude to SQLite

Install: pip install mcp
Run: python 02_database_server.py (then add to Claude Desktop config)
"""
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types
import asyncio
import sqlite3
import json

app = Server("database-mcp")

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
                    "query": {"type": "string", "description": "SQL SELECT query"}
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
                    "threshold": {"type": "integer", "description": "Min stock level", "default": 50}
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
            if not query.strip().upper().startswith("SELECT"):
                return [types.TextContent(type="text", text="Error: Only SELECT queries allowed")]

            cursor = conn.execute(query)
            rows = [dict(row) for row in cursor.fetchall()]

            if not rows:
                return [types.TextContent(type="text", text="No results found")]

            result = f"Found {len(rows)} rows:\n\n" + json.dumps(rows, indent=2)
            return [types.TextContent(type="text", text=result)]

        elif name == "get_low_stock":
            threshold = arguments.get("threshold", 50)
            cursor = conn.execute(
                "SELECT name, stock, price FROM products WHERE stock < ? ORDER BY stock ASC",
                (threshold,)
            )
            rows = [dict(row) for row in cursor.fetchall()]

            if not rows:
                return [types.TextContent(type="text", text=f"All products above {threshold} stock")]

            result = f"⚠️ {len(rows)} products with stock below {threshold}:\n\n"
            for row in rows:
                result += f"• {row['name']}: {row['stock']} units (${row['price']})\n"
            return [types.TextContent(type="text", text=result)]

    except Exception as e:
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    finally:
        conn.close()

    return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

async def main():
    init_db()
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
