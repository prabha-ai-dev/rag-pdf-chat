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
    border: 1px solid #333;
    border-radius: 12px;
    padding: 12px 16px;
    margin: 8px 0;
}
</style>
""", unsafe_allow_html=True)

st.title("📄 PDF Chat")

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

def validate_groq_key(api_key: str):
    try:
        client = Groq(api_key=api_key)

        res = client.chat.completions.create(
            messages=[{"role": "user", "content": "ping"}],
            model="llama-3.3-70b-versatile",
        )

        if not res or not res.choices:
            return False, "No response from API"

        return True, None

    except Exception as e:
        return False, str(e)

def get_groq_answer(query: str, context: str, api_key: str) -> str:
    try:
        client = Groq(api_key=api_key)

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Answer ONLY using the provided context."
                },
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuestion: {query}"
                }
            ],
            model="llama-3.3-70b-versatile",
        )

        return chat_completion.choices[0].message.content.strip()

    except Exception as e:
        return f"❌ API ERROR: {str(e)}"

def answer_question(query: str, retriever, api_key: str):
    try:
        docs = retriever.invoke(query)

        if not docs:
            return "🤔 No relevant info found in the document.", []

        context = "\n\n".join([doc.page_content.strip() for doc in docs])
        answer = get_groq_answer(query, context, api_key)

        return answer, docs

    except Exception as e:
        return f"❌ Error: {str(e)}", []

if not st.session_state.setup_done:

    with st.form("setup_form"):
        st.subheader("Get Started")
        api_key = st.text_input("Groq API Key", type="password")
        uploaded_file = st.file_uploader("Upload PDF", type="pdf")
        submitted = st.form_submit_button("Start Chatting")

    if submitted:
        if not api_key or not uploaded_file:
            st.error("⚠️ Please provide API key and PDF.")
        else:
            with st.spinner("Validating API key..."):
                is_valid, error_msg = validate_groq_key(api_key)

                if not is_valid:
                    st.error(f"❌ Invalid API Key: {error_msg}")
                    st.stop()

                st.success("✅ API Key validated!")

            with st.spinner("Processing PDF..."):

                shutil.rmtree("./chroma_db", ignore_errors=True)

                file_path = f"temp_{uuid.uuid4().hex}.pdf"
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.read())

                loader = PyPDFLoader(file_path)
                docs = loader.load()

                if not docs or all(not doc.page_content.strip() for doc in docs):
                    st.error("❌ Could not extract text from PDF.")
                    os.remove(file_path)
                    st.stop()

                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=600,
                    chunk_overlap=100
                )
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

        if not query:
            st.warning("⚠️ Enter a question.")
            st.stop()

        if len(query.split()) <= 3:
            query = f"Explain from the document: {query}"

        with st.spinner("Thinking..."):
            st.toast("🔍 Searching document...")
            answer, docs = answer_question(
                query,
                st.session_state.retriever,
                st.session_state.groq_key
            )

        # ❗ Handle API errors clearly
        if answer.startswith("❌ API ERROR"):
            st.error(answer)
            st.stop()

        st.session_state.history.append((query, answer))

        if docs:
            with st.expander("📚 Sources"):
                for i, doc in enumerate(docs):
                    st.markdown(f"**Source {i+1}:** {doc.page_content[:200]}...")

        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🔄 Upload a different PDF"):
        st.session_state.clear()
        shutil.rmtree("./chroma_db", ignore_errors=True)
        st.rerun()
