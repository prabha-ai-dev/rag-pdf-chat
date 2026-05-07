import streamlit as st
import tempfile
import shutil
import os

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from groq import Groq


st.set_page_config(
    page_title="Smart PDF Chat",
    layout="wide"
)

st.title("📄 Smart PDF Chat")


GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

if "retriever" not in st.session_state:
    st.session_state.retriever = None

if "history" not in st.session_state:
    st.session_state.history = []


@st.cache_resource
def load_embeddings():

    return HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-en-v1.5",
        encode_kwargs={
            "normalize_embeddings": True
        }
    )

def ask_llm(query, context):

    client = Groq(api_key=GROQ_API_KEY)

    system_prompt = """
You are a smart PDF assistant.

Answer ONLY using the provided context.

Rules:
- Do not make up answers
- If the answer is missing, say:
  "Answer not found in document."
- Keep answers clear and accurate
- Give detailed answers if context contains details
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": f"""
Context:
{context}

Question:
{query}
"""
            }
        ],
        temperature=0.2
    )

    return response.choices[0].message.content.strip()


def get_answer(query, retriever):

    if retriever is None:
        return "📄 Please upload a PDF first.", []

    
    docs = retriever.invoke(query)

    if not docs:
        return "🤔 No relevant information found.", []

    
    docs = docs[:6]

    
    context = "\n\n".join(
        doc.page_content.strip()
        for doc in docs
    )


    answer = ask_llm(query, context)

    return answer, docs

uploaded_file = st.file_uploader(
    "Upload your PDF",
    type="pdf"
)

if uploaded_file:

    with st.spinner("📚 Processing PDF..."):

        
        shutil.rmtree(
            "./chroma_db",
            ignore_errors=True
        )

        
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as tmp:

            tmp.write(uploaded_file.read())
            file_path = tmp.name

        
        loader = PyPDFLoader(file_path)
        documents = loader.load()

        
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=700,
            chunk_overlap=120
        )

        chunks = splitter.split_documents(documents)

        embeddings = load_embeddings()

        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory="./chroma_db"
        )

        retriever = vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": 6
            }
        )

        st.session_state.retriever = retriever

        os.remove(file_path)

        st.success("✅ PDF processed successfully!")

if st.session_state.retriever:

    for q, a in st.session_state.history:

        with st.chat_message("user"):
            st.markdown(q)

        with st.chat_message("assistant"):
            st.markdown(a)

    query = st.chat_input(
        "Ask something from your PDF..."
    )

    if query:

        with st.chat_message("user"):
            st.markdown(query)

        with st.spinner("🤖 Thinking..."):

            answer, docs = get_answer(
                query,
                st.session_state.retriever
            )

        with st.chat_message("assistant"):
            st.markdown(answer)

        st.session_state.history.append(
            (query, answer)
        )

        if docs:

            with st.expander("📚 Retrieved Context"):

                for i, doc in enumerate(docs):

                    st.markdown(f"### Chunk {i+1}")

                    st.write(
                        doc.page_content[:1000]
                    )


if st.button("🔄 Reset App"):

    st.session_state.clear()

    shutil.rmtree(
        "./chroma_db",
        ignore_errors=True
    )

    st.rerun()
