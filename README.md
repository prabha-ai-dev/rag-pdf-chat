Fast RAG PDF Chat:

An AI-powered web app that allows users to upload a PDF and ask questions about its content using Retrieval-Augmented Generation (RAG).

---

Features:

* 📄 Upload any PDF document
* 💬 Ask questions based on the document
* ⚡ Fast responses using optimized models
* 📚 Displays source chunks for transparency
* 🔄 Reset option to clear session

---

Tech Stack:

* Streamlit (UI)
* LangChain (RAG pipeline)
* HuggingFace Transformers (LLM)
* ChromaDB (vector database)
* Sentence Transformers (embeddings)

---

How It Works:

1. The uploaded PDF is loaded and split into smaller chunks
2. Each chunk is converted into embeddings
3. Embeddings are stored in a vector database (ChromaDB)
4. User query is matched with relevant chunks
5. LLM generates an answer using retrieved context

---

Run Locally:

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

Example Questions:

* What is artificial intelligence?
* Explain machine learning
* Summarize the document

---

Limitations:

* Works best when questions are related to document wording
* May fail on very vague or unrelated queries
* Runs on CPU (slower for large PDFs)

---

Future Improvements:

* Better UI (chat bubbles, styling)
* Add conversation memory
* Deploy online for public access
* Improve semantic understanding

---

Built as a beginner AI project to learn RAG, embeddings, and LLM integration.
