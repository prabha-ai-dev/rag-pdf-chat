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