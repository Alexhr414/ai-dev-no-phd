"""
Part 6: MCP Server Tutorial - Example 1
Hello World MCP Server with get_time tool

Install: pip install mcp
Run: python 01_hello_mcp.py (then add to Claude Desktop config)
"""
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types
import asyncio

app = Server("hello-mcp")

@app.list_tools()
async def list_tools() -> list[types.Tool]:
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
