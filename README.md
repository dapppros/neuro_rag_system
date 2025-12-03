# Neurophysiology RAG System 🧠

A Retrieval-Augmented Generation system built with Python and Gemini 1.5. This tool allows users to upload Neurophysiology textbooks (PDFs) and ask complex medical questions, receiving answers grounded strictly in the source text.

**Last Updated:** ## Features
* **Multi-Book Support:** Upload multiple PDFs into the context window.
* **Long Context:** Leverages Gemini 1.5's 1M+ token window to read entire books.
* **Secure:** Environment variable management for API keys.

## Setup
1.  Install `uv`: `curl -LsSf https://astral.sh/uv/install.sh | sh`
2.  Install dependencies: `uv pip install google-generativeai python-dotenv rich`
3.  Create `.env` file and add `GOOGLE_API_KEY=...`

## Usage
Run the system:
```bash
python rag_system.py
