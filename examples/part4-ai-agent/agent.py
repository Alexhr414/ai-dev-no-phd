#!/usr/bin/env python3
"""
AI Agent with Tool Calling
Tutorial: https://github.com/Alexhr414/ai-dev-no-phd/blob/main/ai-agent-tutorial.md

This agent can:
- Search the web for real-time information
- Get current weather for any city
- Execute Python code safely
- Chain multiple tools together

Usage:
    python agent.py "What's the weather in Tokyo?"
    python agent.py "Search for latest AI news"
    python agent.py "Calculate fibonacci(15)"
    python agent.py interactive  # Interactive mode
"""

import os
import sys
import json
import requests
from typing import List, Dict, Any, Optional
from openai import OpenAI

# Tool definitions
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the web for current information using DuckDuckGo",
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
            "description": "Get current weather for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city name (e.g., 'Tokyo', 'London')"
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
            "description": "Execute Python code and return the result. Use for calculations, data processing, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python code to execute (must print the result)"
                    }
                },
                "required": ["code"]
            }
        }
    }
]

# Tool implementations
def search_web(query: str) -> str:
    """Search the web using DuckDuckGo Instant Answer API."""
    try:
        url = f"https://api.duckduckgo.com/?q={query}&format=json"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        # Extract relevant info
        abstract = data.get("AbstractText", "")
        if abstract:
            return f"Search result: {abstract}"
        
        # Try related topics
        topics = data.get("RelatedTopics", [])
        if topics and len(topics) > 0:
            first = topics[0]
            if isinstance(first, dict) and "Text" in first:
                return f"Search result: {first['Text']}"
        
        return "No relevant results found. Try rephrasing your query."
    except Exception as e:
        return f"Search error: {str(e)}"

def get_weather(city: str) -> str:
    """Get current weather using wttr.in API."""
    try:
        # wttr.in provides weather data in JSON format
        url = f"https://wttr.in/{city}?format=j1"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        current = data["current_condition"][0]
        temp_c = current["temp_C"]
        desc = current["weatherDesc"][0]["value"]
        humidity = current["humidity"]
        
        return f"Weather in {city}: {temp_c}°C, {desc}, Humidity: {humidity}%"
    except Exception as e:
        return f"Weather error: {str(e)}"

def run_python(code: str) -> str:
    """Execute Python code in a restricted environment."""
    import subprocess
    try:
        # Whitelist safe operations
        if any(dangerous in code.lower() for dangerous in ["import os", "import sys", "exec", "eval", "open", "__"]):
            return "Error: Code contains potentially dangerous operations"
        
        # Run code with timeout
        result = subprocess.run(
            ["python3", "-c", code],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            return result.stdout.strip() or "Code executed successfully (no output)"
        else:
            return f"Error: {result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return "Error: Code execution timeout (5s limit)"
    except Exception as e:
        return f"Execution error: {str(e)}"

# Map function names to implementations
TOOL_FUNCTIONS = {
    "search_web": search_web,
    "get_weather": get_weather,
    "run_python": run_python
}

class Agent:
    """AI Agent with tool calling capabilities."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model
        self.conversation_history: List[Dict[str, Any]] = []
    
    def run(self, user_message: str, verbose: bool = False) -> str:
        """Run the agent with a user message."""
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        max_iterations = 5  # Prevent infinite loops
        for iteration in range(max_iterations):
            if verbose:
                print(f"\n[Iteration {iteration + 1}]")
            
            # Call OpenAI with tools
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.conversation_history,
                tools=TOOLS,
                tool_choice="auto"
            )
            
            message = response.choices[0].message
            
            # If no tool calls, we have the final answer
            if not message.tool_calls:
                self.conversation_history.append({
                    "role": "assistant",
                    "content": message.content
                })
                return message.content
            
            # Execute tool calls
            self.conversation_history.append({
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in message.tool_calls
                ]
            })
            
            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                if verbose:
                    print(f"Calling tool: {function_name}({function_args})")
                
                # Execute the tool
                function = TOOL_FUNCTIONS[function_name]
                result = function(**function_args)
                
                if verbose:
                    print(f"Tool result: {result[:100]}...")
                
                # Add tool result to history
                self.conversation_history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })
        
        return "Error: Maximum iterations reached"
    
    def reset(self):
        """Clear conversation history."""
        self.conversation_history = []

def main():
    """CLI interface for the agent."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not set")
        print("Set it with: export OPENAI_API_KEY=sk-your-key-here")
        sys.exit(1)
    
    agent = Agent()
    
    # Interactive mode
    if sys.argv[1] == "interactive":
        print("AI Agent Interactive Mode")
        print("Available tools: search_web, get_weather, run_python")
        print("Type 'exit' to quit, 'reset' to clear history\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                if not user_input:
                    continue
                
                if user_input.lower() == "exit":
                    break
                
                if user_input.lower() == "reset":
                    agent.reset()
                    print("Conversation history cleared.\n")
                    continue
                
                response = agent.run(user_input, verbose=False)
                print(f"\nAgent: {response}\n")
            
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}\n")
    
    # Single query mode
    else:
        query = " ".join(sys.argv[1:])
        verbose = "--verbose" in sys.argv or "-v" in sys.argv
        query = query.replace("--verbose", "").replace("-v", "").strip()
        
        print(f"Query: {query}\n")
        response = agent.run(query, verbose=verbose)
        print(f"Response: {response}")

if __name__ == "__main__":
    main()
