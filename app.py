import streamlit as st
import tempfile
import shutil
import os

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from groq import Groq


st.set_page_config(page_title="Smart PDF Chat", layout="wide")

st.title("📄 Smart PDF Chat")


GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("❌ GROQ_API_KEY missing in Streamlit Secrets")
    st.stop()


if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None

if "history" not in st.session_state:
    st.session_state.history = []


@st.cache_resource
def load_embeddings():

    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


def ask_llm(question, context):

    client = Groq(api_key=GROQ_API_KEY)

    prompt = f"""
You are a helpful PDF assistant.

Use ONLY the provided context.

If answer is not found in context,
say:
"Answer not found in document."

Context:
{context}

Question:
{question}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    return response.choices[0].message.content

def process_pdf(uploaded_file):

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    ) as tmp_file:

        tmp_file.write(uploaded_file.read())

        temp_path = tmp_file.name

    loader = PyPDFLoader(temp_path)

    documents = loader.load()

    os.remove(temp_path)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )

    chunks = splitter.split_documents(documents)

    embeddings = load_embeddings()

    persist_dir = tempfile.mkdtemp()

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_dir
    )

    return vectorstore, persist_dir


def get_answer(question):

    if st.session_state.vectorstore is None:
        return "📄 Upload PDF first.", []

    try:

        docs = st.session_state.vectorstore.similarity_search(
            question,
            k=4
        )

    except Exception as e:

        return f"⚠️ Retrieval Error: {str(e)}", []

    if not docs:
        return "🤔 No relevant information found.", []

    context = "\n\n".join(
        [doc.page_content for doc in docs]
    )

    answer = ask_llm(question, context)

    return answer, docs


uploaded_file = st.file_uploader(
    "Upload your PDF",
    type="pdf"
)

if uploaded_file:

    if st.session_state.vectorstore is None:

        with st.spinner("📚 Processing PDF..."):

            try:

                vectorstore, persist_dir = process_pdf(
                    uploaded_file
                )

                st.session_state.vectorstore = vectorstore

                st.session_state.persist_dir = persist_dir

                st.success(
                    "✅ PDF processed successfully!"
                )

            except Exception as e:

                st.error(
                    f"❌ Error processing PDF: {str(e)}"
                )

if st.session_state.vectorstore is not None:

    for q, a in st.session_state.history:

        with st.chat_message("user"):
            st.markdown(q)

        with st.chat_message("assistant"):
            st.markdown(a)

    question = st.chat_input(
        "Ask something from your PDF..."
    )

    if question:

        with st.chat_message("user"):
            st.markdown(question)

        with st.spinner("🤖 Thinking..."):

            answer, docs = get_answer(question)

        with st.chat_message("assistant"):
            st.markdown(answer)

        st.session_state.history.append(
            (question, answer)
        )

        if docs:

            with st.expander(
                "📚 Retrieved Context"
            ):

                for i, doc in enumerate(docs):

                    st.markdown(
                        f"### Chunk {i+1}"
                    )

                    st.write(
                        doc.page_content[:1000]
                    )


if st.button("🔄 Reset App"):

    try:

        if "persist_dir" in st.session_state:

            shutil.rmtree(
                st.session_state.persist_dir,
                ignore_errors=True
            )

    except:
        pass

    st.session_state.clear()

    st.rerun()
