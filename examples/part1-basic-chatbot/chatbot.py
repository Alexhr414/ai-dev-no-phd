#!/usr/bin/env python3
"""
AI Development Without a PhD - Part 1: Basic Chatbot
A minimal chatbot using OpenAI's Chat Completions API.

Based on the tutorial: https://github.com/Alexhr414/ai-dev-no-phd/blob/main/ai-chatbot-tutorial.md
"""

import os
from openai import OpenAI

# Initialize the OpenAI client
# Expects OPENAI_API_KEY environment variable to be set
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def chat(user_message, conversation_history=None):
    """
    Send a message to the chatbot and get a response.
    
    Args:
        user_message (str): The user's message
        conversation_history (list, optional): List of previous messages for context
    
    Returns:
        tuple: (response_text, updated_conversation_history)
    """
    if conversation_history is None:
        conversation_history = []
    
    # Add the user's message to history
    conversation_history.append({
        "role": "user",
        "content": user_message
    })
    
    # Call the OpenAI API
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Using the cost-effective mini model
        messages=conversation_history,
        temperature=0.7,  # Controls randomness (0=deterministic, 1=creative)
        max_tokens=500    # Limit response length
    )
    
    # Extract the assistant's reply
    assistant_message = response.choices[0].message.content
    
    # Add assistant's response to history
    conversation_history.append({
        "role": "assistant",
        "content": assistant_message
    })
    
    return assistant_message, conversation_history


def main():
    """Simple command-line chatbot interface."""
    print("🤖 AI Chatbot (type 'quit' to exit)\n")
    
    conversation_history = []
    
    while True:
        user_input = input("You: ")
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("👋 Goodbye!")
            break
        
        if not user_input.strip():
            continue
        
        try:
            response, conversation_history = chat(user_input, conversation_history)
            print(f"\nBot: {response}\n")
        except Exception as e:
            print(f"❌ Error: {e}\n")


if __name__ == "__main__":
    main()
