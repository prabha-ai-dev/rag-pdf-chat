<<<<<<< HEAD
import streamlit as st
import uuid
import shutil
import os

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from groq import Groq



st.set_page_config(page_title="PDF Chat", layout="centered")

st.markdown("""
    <style>
        #MainMenu, footer, header {visibility: hidden;}
        .block-container {padding-top: 2rem; max-width: 700px;}

        .chat-bubble-user {
            background: #2a2a2a;
            color: #ffffff;
            border-radius: 12px;
            padding: 12px 16px;
            margin: 8px 0;
            text-align: right;
        }
        .chat-bubble-ai {
            background: #1e1e1e;
            color: #ffffff;
            border: 1px solid #333333;
            border-radius: 12px;
            padding: 12px 16px;
            margin: 8px 0;
        }
    </style>
""", unsafe_allow_html=True)

st.title("PDF Chat")



if "retriever" not in st.session_state:
    st.session_state.retriever = None

if "history" not in st.session_state:
    st.session_state.history = []

if "groq_key" not in st.session_state:
    st.session_state.groq_key = None

if "setup_done" not in st.session_state:
    st.session_state.setup_done = False



@st.cache_resource
def load_embeddings():
    return HuggingFaceEmbeddings(
        model_name="BAAI/bge-base-en-v1.5",
        encode_kwargs={"normalize_embeddings": True}
    )



def get_groq_answer(query: str, context: str, api_key: str) -> str:
    client = Groq(api_key=api_key)
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant. Answer the user's question "
                    "using ONLY the context provided. If the answer is not in "
                    "the context, say 'I don't know based on the document.'"
                )
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {query}"
            }
        ],
        model="llama-3.3-70b-versatile",
    )
    return chat_completion.choices[0].message.content.strip()



def answer_question(query: str, retriever, api_key: str):
    docs = retriever.get_relevant_documents(query)
    if not docs:
        return "I don't know based on the document."
    context = "\n\n".join([doc.page_content.strip() for doc in docs])
    return get_groq_answer(query, context, api_key)



if not st.session_state.setup_done:

    with st.form("setup_form"):
        st.subheader("Get Started")
        api_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...")
        uploaded_file = st.file_uploader("Upload PDF", type="pdf")
        submitted = st.form_submit_button("Start Chatting")

    if submitted:
        if not api_key or not uploaded_file:
            st.error("Please provide both your Groq API key and a PDF file.")
        else:
            with st.spinner("Processing PDF..."):
                shutil.rmtree("./chroma_db", ignore_errors=True)

                file_path = f"temp_{uuid.uuid4().hex}.pdf"
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.read())

                loader = PyPDFLoader(file_path)
                docs = loader.load()

                splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100)
                chunks = splitter.split_documents(docs)

                embeddings = load_embeddings()
                vectorstore = Chroma.from_documents(
                    documents=chunks,
                    embedding=embeddings,
                    persist_directory="./chroma_db"
                )
                vectorstore.persist()

                st.session_state.retriever = vectorstore.as_retriever(
                    search_type="similarity",
                    search_kwargs={"k": 3}
                )
                st.session_state.groq_key = api_key
                st.session_state.setup_done = True

                os.remove(file_path)
                st.rerun()



else:

    
    for q, a in st.session_state.history:
        st.markdown(f'<div class="chat-bubble-user">{q}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="chat-bubble-ai">{a}</div>', unsafe_allow_html=True)


    query = st.chat_input("Ask a question about your PDF...")

    if query:
        query = query.strip()
        if len(query.split()) <= 3:
            query = f"What does the document say about {query}?"

        with st.spinner("Thinking..."):
            answer = answer_question(
                query,
                st.session_state.retriever,
                st.session_state.groq_key
            )

        st.session_state.history.append((query, answer))
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Upload a different PDF"):
        st.session_state.clear()
        shutil.rmtree("./chroma_db", ignore_errors=True)
        st.rerun()
=======
import streamlit as st
import os
import uuid

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from langchain_community.llms import HuggingFacePipeline


#  UI 
st.set_page_config(page_title="Fast RAG PDF Chat", layout="wide")
st.title("⚡ Fast RAG PDF Chat")

uploaded_file = st.file_uploader("Upload PDF", type="pdf")


# SESSION 
if "history" not in st.session_state:
    st.session_state.history = []

if "qa_chain" not in st.session_state:
    st.session_state.qa_chain = None


#  CACHE 
@st.cache_resource
def load_llm():
    tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-small")
    model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-small")

    pipe = pipeline(
        "text2text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=100,   # faster
        do_sample=False
    )

    return HuggingFacePipeline(pipeline=pipe)


@st.cache_resource
def load_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


if uploaded_file and st.session_state.qa_chain is None:

    with st.spinner("⚙️ Processing PDF... please wait"):
        
        # Save PDF
        file_path = f"temp_{uuid.uuid4().hex}.pdf"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())

        
        loader = PyPDFLoader(file_path)
        documents = loader.load()

        
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=50
        )
        docs = splitter.split_documents(documents)

    
        embeddings = load_embeddings()

        
        persist_directory = f"./db_{uuid.uuid4().hex}"

        vectorstore = Chroma.from_documents(
            docs,
            embedding=embeddings,
            persist_directory=persist_directory
        )

        retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        )

        llm = load_llm()

        prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""
You are a helpful AI assistant.

Answer ONLY from the given context.
If answer is not found, say:
"I don't know based on the document."

Context:
{context}

Question:
{question}

Answer:
"""
        )

        
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt}
        )

        st.session_state.qa_chain = qa_chain

        st.success("✅ PDF processed! Ask your questions.")


if st.session_state.qa_chain:

    query = st.text_input("💬 Ask a question")

    if query:
        with st.spinner("🤖 Thinking..."):
            result = st.session_state.qa_chain.invoke({"query": query})

        answer = result["result"]
        sources = result["source_documents"]

        st.session_state.history.append((query, answer, sources))

    for q, a, sources in st.session_state.history:
        st.markdown(f"**🧑 You:** {q}")
        st.markdown(f"**🤖 AI:** {a}")

        with st.expander("📚 Sources"):
            for doc in sources:
                st.write(doc.page_content[:200])

if st.button("🔄 Reset App"):
    st.session_state.clear()
    st.rerun()
>>>>>>> 11eb601c206bf8a4707a0c84b14762b53e33a80a
