# Part 1: Basic Chatbot Example

A minimal, working chatbot using OpenAI's Chat Completions API.

## What You'll Learn

- How to use the OpenAI Python SDK
- Message history management for context
- Basic conversation flow
- Error handling and API calls

## Prerequisites

```bash
pip install openai
```

## Setup

1. Get your OpenAI API key from https://platform.openai.com/api-keys
2. Set it as an environment variable:

```bash
export OPENAI_API_KEY="sk-proj-..."
```

## Usage

Run the chatbot:

```bash
python chatbot.py
```

Example conversation:
```
🤖 AI Chatbot (type 'quit' to exit)

You: What is Python?
Bot: Python is a high-level, interpreted programming language...

You: Can you give me a simple code example?
Bot: Sure! Here's a classic "Hello, World!" example:
...

You: quit
👋 Goodbye!
```

## How It Works

1. **Client Initialization**: Creates an OpenAI client with your API key
2. **Message History**: Maintains conversation context in a list
3. **API Call**: Sends messages to GPT-4o-mini model
4. **Response Extraction**: Gets the assistant's reply
5. **History Update**: Adds both user and assistant messages to history

## Key Parameters

- `model`: Which AI model to use (gpt-4o-mini is cost-effective)
- `temperature`: Controls randomness (0-1, higher = more creative)
- `max_tokens`: Limits response length to control costs

## Cost Optimization

This example uses `gpt-4o-mini` instead of full GPT-4 to keep costs low while learning:
- gpt-4o-mini: ~$0.15 per 1M input tokens
- gpt-4o: ~$2.50 per 1M input tokens

## Next Steps

Once you're comfortable with this basic chatbot:
- Add a system message to set personality/behavior
- Implement streaming responses for real-time output
- Add function calling for tool use
- Build a RAG system (Part 2)

## Full Tutorial

Read the complete tutorial: [AI Chatbot Tutorial](../../ai-chatbot-tutorial.md)

## Troubleshooting

**"No API key found"**: Make sure `OPENAI_API_KEY` environment variable is set
**Rate limit errors**: Wait a few seconds between requests, or upgrade your OpenAI plan
**Import errors**: Run `pip install openai` to install the SDK
