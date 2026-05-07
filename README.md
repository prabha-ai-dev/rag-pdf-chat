📄 Smart PDF Chat:

> An AI-powered RAG application that lets you upload PDFs and chat with them intelligently using semantic search and Large Language Models.

---

Overview:

Smart PDF Chat is an advanced Retrieval-Augmented Generation (RAG) application built with Streamlit, LangChain, ChromaDB, HuggingFace Embeddings, and Groq LLMs.

Upload any PDF and ask questions in natural language.  
The app retrieves the most relevant document chunks and generates accurate AI-powered answers instantly.

---

Features:

✅ Upload and analyze PDF documents  
✅ Intelligent AI question answering  
✅ Semantic search using vector embeddings  
✅ Fast responses powered by Groq LLM  
✅ ChromaDB vector database integration  
✅ Interactive chat interface  
✅ Displays retrieved document context  
✅ Hallucination-controlled responses  
✅ Secure API handling with Streamlit Secrets  
✅ Deploy-ready architecture

---

How It Works:

```text
PDF Upload
    ↓
Text Extraction
    ↓
Chunking
    ↓
Embeddings Generation
    ↓
Chroma Vector Database
    ↓
Semantic Retrieval
    ↓
Groq LLM Response
```

The app uses Retrieval-Augmented Generation (RAG) to answer questions directly from your uploaded document.

---

Tech Stack:

| Technology | Purpose |
|---|---|
| Streamlit | Web Interface |
| LangChain | RAG Pipeline |
| ChromaDB | Vector Database |
| HuggingFace Embeddings | Semantic Embeddings |
| Groq API | Large Language Model |
| Python | Backend Logic |

---

Project Structure:

```bash
smart-pdf-chat/
│
├── streamlitapp.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── .streamlit/
│   └── secrets.toml
│
└── chroma_db/
```

---

Installation:

Clone Repository:

```bash
git clone https://github.com/your-username/smart-pdf-chat.git
cd smart-pdf-chat
```

---

Install Dependencies:

```bash
pip install -r requirements.txt
```

---

Configure API Key:

Create a file:

```bash
.streamlit/secrets.toml
```

Add your Groq API key:

```toml
GROQ_API_KEY="your_groq_api_key"
```

---

Run the Application:

```bash
streamlit run streamlitapp.py
```

---

Application Highlights:

- Upload PDFs instantly  
- AI-generated accurate answers  
- Retrieved context visualization  
- Fast semantic search  
- Smart Retrieval-Augmented Generation

---

Future Improvements:

- Multi-PDF support
- Chat memory
- Page number citations
- Streaming responses
- OCR for scanned PDFs
- Better UI/UX
- Hybrid search
- Dark mode support

---

Security:

Sensitive API keys are securely handled using:

- Streamlit Secrets
- `.gitignore`
- Environment-safe deployment

---

Deployment:

This project is fully deployable on:

- Streamlit Cloud
- Render
- Railway

---

Author:

Built with passion for AI Engineering and RAG Applications.

---

License:

This project is licensed under the MIT License.

---

Support:

If you like this project:

⭐ Star the repository  
🍴 Fork the project  
🚀 Share with others
