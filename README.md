
# 🤖 Wikipedia Search Agent

An AI-powered Wikipedia research assistant that uses Gemini
and the Wikipedia API to search, analyze, and summarize
Wikipedia information.

## Features

- 🔎 Intelligent Wikipedia search
- 🤖 Gemini-powered AI agent
- 🧠 Function/tool calling
- 📚 Relevant article selection
- 💬 Conversation memory
- 🔗 Wikipedia source attribution
- ⚠️ Error handling
- 🎨 Streamlit web interface

## Architecture

User
↓
Gemini AI Agent
↓
Wikipedia Search Tool
↓
Multiple Wikipedia Results
↓
Relevant Article Selection
↓
Wikipedia Content
↓
Gemini
↓
Final Answer + Source

## Technologies

- Python
- Google Gemini API
- Wikipedia API
- Streamlit
- Google Colab

## How It Works

1. User asks a question.
2. Gemini analyzes the question.
3. Gemini decides whether Wikipedia is required.
4. The Wikipedia search tool is called.
5. Multiple relevant articles are retrieved.
6. The most relevant article is selected.
7. Wikipedia information is returned to Gemini.
8. Gemini generates the final answer.
9. The Wikipedia source is displayed.

## Installation

```bash
pip install -r requirements.txt
