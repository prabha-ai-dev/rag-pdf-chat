PDF Chat (RAG-based Chatbot):

An AI-powered web app that allows users to upload a PDF and ask questions about its content using Retrieval-Augmented Generation (RAG).

---

Features:

- Upload any PDF document
- Ask questions based on the document
- Context-aware answers using semantic search
- Displays source chunks for transparency
- Fast responses using Groq LLM
- Handles invalid API keys and errors gracefully
- Handles irrelevant queries intelligently

---

Tech Stack:

- Python
- Streamlit (UI)
- LangChain (RAG pipeline)
- Chroma (Vector Database)
- HuggingFace Embeddings (BAAI/bge-base-en-v1.5)
- Groq API (LLM inference)

---

How It Works:

1. User uploads a PDF
2. Text is extracted and split into chunks
3. Chunks are converted into embeddings
4. Stored in Chroma vector database
5. User asks a question
6. Relevant chunks are retrieved
7. LLM generates answer based on context

---

Run Locally:

```bash
git clone https://github.com/your-username/pdf-rag-chatbot.git
cd pdf-rag-chatbot
pip install -r requirements.txt
streamlit run app.py

---

Notes:

This project demonstrates practical implementation of Retrieval-Augmented Generation (RAG) including:

document understanding
semantic search
context-aware response generation

---

Future Improvements:

Add support for multiple PDFs
Add chat memory across sessions
Improve retrieval with hybrid search
Add streaming responses (typing effect)

---

Deployment:

This app can be deployed easily on Streamlit Cloud.

---

Author:

prabha
