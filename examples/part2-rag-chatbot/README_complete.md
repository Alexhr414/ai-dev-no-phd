# Part 2: RAG Chatbot

**Add document expertise to your AI chatbot with Retrieval-Augmented Generation (RAG).**

Part of the [AI Development Without a PhD](https://github.com/Alexhr414/ai-dev-no-phd) tutorial series.

## What This Does

Turn your chatbot into an expert on **your own documents**:
- ✅ Loads PDFs, text files, and markdown files
- ✅ Splits documents into searchable chunks
- ✅ Retrieves relevant context for each question
- ✅ Answers questions grounded in your documents
- ✅ Shows which sources were consulted

## Prerequisites

- Python 3.9+
- OpenAI API key

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set your OpenAI API key
export OPENAI_API_KEY='your-key-here'
```

## Usage

```bash
# Create a folder for your documents
mkdir sample_docs

# Add some PDFs, .txt, or .md files to sample_docs/

# Run the chatbot
python rag_chatbot.py
```

The chatbot will:
1. Load all documents from `sample_docs/`
2. Create embeddings and index them
3. Start an interactive chat where you can ask questions about your documents

## Example Interaction

```
You: What does the contract say about payment terms?

[Sources consulted: contract.pdf]