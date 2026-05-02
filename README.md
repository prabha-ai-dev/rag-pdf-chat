RAG PDF Chat

An AI-powered web app that lets you upload a PDF and chat with it using Retrieval-Augmented Generation (RAG) + Groq LLM.

---

Features:

-  Upload any PDF document  
-  Ask questions about the content  
-  Supports **single-word queries** (auto-expanded for better answers)  
-  Fast responses using **Groq LLM (Llama 3.3 70B)**  
-  Semantic search with embeddings  
-  Clean chat UI with conversation history  
-  Reset option to upload a new PDF  

---

Tech Stack:

Streamlit – UI  
LangChain – RAG pipeline  
ChromaDB – Vector database  
HuggingFace Embeddings (BAAI/bge-base-en-v1.5)  
Groq API (Llama 3.3 70B) – Answer generation  

---

How It Works:

1. Upload a PDF  
2. Text is split into chunks  
3. Chunks are converted into embeddings  
4. Stored in Chroma vector database  
5. User query retrieves relevant chunks  
6. Groq LLM generates answer from context  

---

Run Locally

git clone https://github.com/prabha-ai-dev/fast-rag-pdf-chat
cd fast-rag-pdf-chat

---

Usage:

Enter your Groq API Key
Upload a PDF
Start asking questions


---

Example Queries:

What is artificial intelligence?
machine learning
embeddings
summarize this document

---

Example Queries:

What is artificial intelligence?
machine learning
embeddings
summarize this document

---

Project Note

Built as a hands-on project to learn:

RAG pipelines
Embeddings & vector search
LLM API integration
Real-world AI app development

---

What changed :

used Groq (modern LLM) 
improved query handling (single-word support)  
built a chat-style UI  
understand RAG pipeline clearly
